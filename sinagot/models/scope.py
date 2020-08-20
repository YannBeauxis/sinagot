# coding=utf-8

from importlib import import_module
from typing import Optional, Generator
import pandas as pd
from sinagot.utils import get_module, get_plugin_modules
from sinagot.models import Model


class Scope(Model):
    """
    A Scope instance can :

    - Handle task and modality subscopes.

    - Handle StepCollection with `.steps` attribute.

    Note:
        Scope is base class for [RecordCollection](record_collection.md) and [Record](record.md).
    """

    _REPR_ATTRIBUTES = ["task", "modality"]
    _MODEL_TYPE = None
    _subscope_class = None
    _tasks = []
    task = None
    _modalities = []
    modality = None

    def __init__(
        self,
        workspace: "Workspace",
        task: Optional[str] = None,
        modality: Optional[str] = None,
    ):
        """
        Args:
            workspace: Root Workspace.
            task: Task of the scope.
            modality: Modality of the scope.
        """

        workspace.logger.debug(
            "## init scope for %s. _subscope_class: %s", self, self._subscope_class
        )
        if task is not None:
            self.task: Optional[str] = task
            """Task of the scope. If `None`, the scope represents all available tasks."""
        if modality is not None:
            self.modality: Optional[str] = modality
            """Modality of the scope. If `None`, the scope represents all available modalities."""
        if self._subscope_class is None:
            self._subscope_class = self.__class__
        super().__init__(workspace)

    def _get_repr_attributes(self):
        attributes = super()._get_repr_attributes()
        if not self.workspace.is_unit_mode:
            for attribute in ["task", "modality"]:
                if attribute not in attributes:
                    attributes.append(attribute)
        return attributes

    @classmethod
    def _set_subscopes(cls, workspace):
        """Create subscope tasks and modalities attributes
        Run once at workspace initialization"""

        SUBSCOPES = (
            ("task", "tasks"),
            ("modality", "modalities"),
        )

        for subscope, collection in SUBSCOPES:
            if collection in workspace.config:
                setattr(
                    cls,
                    "_{}".format(collection),
                    [
                        cls._add_subscope(
                            subscope=subscope, value=value, workspace=workspace
                        )
                        for value in workspace.config[collection].keys()
                    ],
                )

    @classmethod
    def _add_subscope(cls, subscope, value, workspace):
        """Add subscope to self.__class__ as a property
        that call an instance of local defined subclass"""

        _subscope_class = cls._search_custom_subscope_in_config(
            subscope, value, workspace
        )
        subscope_access = property(
            cls._property_factory(_subscope_class, subscope, value)
        )
        setattr(
            cls, value, subscope_access,
        )
        return value

    @classmethod
    def _search_custom_subscope_in_config(cls, subscope, value, workspace):
        model_type = cls._MODEL_TYPE
        if subscope == "modality":

            sub_config = workspace.config
            for key in ("modalities", value, "models"):
                sub_config = sub_config.get(key, {})

            custom_class = cls._get_custom_class(workspace, value)
            if custom_class:
                return custom_class

            plugin_model = sub_config.get("plugin")
            if plugin_model:
                return get_plugin_modules(plugin_model)[model_type]
        return cls

    @classmethod
    def _get_custom_class(cls, workspace, value):
        model_type = cls._MODEL_TYPE
        base_class_name = model_type.title().replace("_", "")
        try:
            custom_class = get_module(
                workspace, base_class_name, value, "models", model_type
            )
        except FileNotFoundError:
            return None
        custom_class.__name__ = value.title() + base_class_name
        if model_type == "record_collection":
            record_class = custom_class._record_class._get_custom_class(
                workspace, value
            )
            if record_class:
                custom_class._record_class = record_class
        return custom_class

    @staticmethod
    def _property_factory(_subscope_class, subscope, value):
        def get(self):
            if self._is_valid_subscope(subscope, value):
                kwargs = {
                    "workspace": self.workspace,
                    "task": self.task,
                    "modality": self.modality,
                }
                kwargs[subscope] = value
                if self._MODEL_TYPE == "record":
                    kwargs["record_id"] = self.id
                return _subscope_class(**kwargs)
            else:
                raise AttributeError(
                    "{} {} is not valid for {}".format(subscope, value, self)
                )

        return get

    def _is_valid_subscope(self, subscope, value):
        if getattr(self, subscope) is not None:
            return False
        if subscope == "task":
            return self.modality in self.workspace.config["tasks"][value][
                "modalities"
            ] + [None]
        elif subscope == "modality":
            return (
                self.task is None
                or value in self.workspace.config["tasks"][self.task]["modalities"]
            )
        else:
            return False

    @property
    def is_unit(self) -> bool:
        """Check if has both task and modality not `None`."""

        return not (self.task is None or self.modality is None)

    def get_subscope(
        self, task: Optional[str] = None, modality: Optional[str] = None
    ) -> "Scope":
        """Get subscope for given task and/or modality

        Args:
            task : the task target
            modality : the modality target

        Returns:
            [type]: [description]
        """
        result = self
        if task:
            result = getattr(result, task)
        if modality:
            result = getattr(result, modality)
        return result

    def iter_units(self) -> Generator["Scope", None, None]:
        """
        Generate each 'unit' subscopes of the current scope,
        i.e. subscope with specific task and modality

        Returns:
            Subscope with a task attribute.
        """

        if self.task is None:
            tasks = self.iter_tasks()
        else:
            tasks = [self]
        for task in tasks:
            if task.modality is None:
                modalities = task.iter_modalities()
            else:
                modalities = [task]
            for modality in modalities:
                yield modality

    def iter_tasks(self) -> Generator["Scope", None, None]:
        """
        Generate subscopes of the current scope for each of its task.

        Returns:
            Subscope with a task attribute.
        """

        for task in self._tasks:
            if self._is_valid_subscope("task", task):
                model = getattr(self, task)
                yield model

    def iter_modalities(self) -> Generator["Scope", None, None]:
        """
        Generate subscopes of the current scope for each of its modalities.

        Returns:
            Subscope with a modality attribute.
        """

        for modality in self._modalities:
            if self._is_valid_subscope("modality", modality):
                yield getattr(self, modality)

    def count_detail(self, *args, **kwargs):

        if self.is_unit:
            df = self._count_detail_unit(*args, **kwargs)
        else:
            df = pd.concat(
                [unit.count_detail(*args, **kwargs) for unit in self.iter_units()]
            )
        df.reset_index(drop=True, inplace=True)
        return df

    def _count_detail_unit(self):
        return pd.DataFrame()
