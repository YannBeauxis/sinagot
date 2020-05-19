# coding=utf-8

from typing import Optional, Generator, TypeVar
import pandas as pd
from sinagot.models import Model, StepCollection


class Scope(Model):
    # """
    # A Scope instance can :

    # - Handle task and modality subscopes.

    # - Handle StepCollection with `.steps` attribute.

    # Note:
    #     Scope is base class for [RecordCollection](record_collection.md) and [Record](record.md).
    # """

    _REPR_ATTRIBUTES = ["task", "modality"]
    _MODEL_TYPE = None
    _DEPRECATED_MODEL_TYPES = {"subset": "record_collection"}
    _subscope_class = None
    _tasks = []
    task = None
    _modalities = []
    modality = None

    def __init__(
        self,
        dataset: "Dataset",
        task: Optional[str] = None,
        modality: Optional[str] = None,
    ):
        """
        Args:
            dataset: Root Dataset.
            task: Task of the scope.
            modality: Modality of the scope.
        """

        dataset.logger.debug(
            "## init scope for %s. _subscope_class: %s", self, self._subscope_class
        )
        if task is not None:
            self.task: str = task
            """Task of the scope. If `None`, the scope represents all available tasks."""
        if modality is not None:
            self.modality: str = modality
            """Modality of the scope. If `None`, the scope represents all available modalities."""
        if self._subscope_class is None:
            self._subscope_class = self.__class__
        super().__init__(dataset)

        self.steps: "StepCollection" = self._set_step_collection()
        """Collection of steps."""

    @classmethod
    def _set_subscopes(cls, dataset):
        """Create subscope tasks and modalities attributes
        Run once at dataset initialization"""

        SUBSCOPES = (
            ("task", "tasks"),
            ("modality", "modalities"),
        )

        for subscope, collection in SUBSCOPES:
            setattr(
                cls,
                "_{}".format(collection),
                [
                    cls._add_subscope(subscope=subscope, value=value, dataset=dataset)
                    for value in dataset.config[collection].keys()
                ],
            )

    @classmethod
    def _add_subscope(cls, subscope, value, dataset):
        """Add subscope to self.__class__ as a property
        that call an instance of local defined subclass"""

        _subscope_class = cls._search_custom_subscope_in_config(
            subscope, value, dataset
        )
        setattr(
            cls,
            value,
            property(cls._property_factory(_subscope_class, subscope, value)),
        )
        return value

    @classmethod
    def _search_custom_subscope_in_config(cls, subscope, value, dataset):
        model_type = cls._MODEL_TYPE
        if subscope == "modality":
            sub_config = dataset.config
            for key in ("modalities", value, "models"):
                sub_config = sub_config.get(key, {})
            custom_class, model_type = cls._DEPRECATED_get_model_type_from_config(
                sub_config, model_type
            )
            if custom_class:
                return dataset._get_module(custom_class, value, "models", model_type)
        return cls

    #  TODO: Deprecated warning
    @classmethod
    def _DEPRECATED_get_model_type_from_config(cls, sub_config, model_type):
        for key in sub_config.keys():
            if cls._DEPRECATED_MODEL_TYPES.get(key) == model_type:
                return sub_config[key], key
        return sub_config.get(model_type), model_type

    @staticmethod
    def _property_factory(_subscope_class, subscope, value):
        def get(self):
            if self._is_valid_subscope(subscope, value):
                kwargs = {
                    "dataset": self.dataset,
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
            return self.modality in self.dataset.config["tasks"][value][
                "modalities"
            ] + [None]
        elif subscope == "modality":
            return (
                self.task is None
                or value in self.dataset.config["tasks"][self.task]["modalities"]
            )
        else:
            return False

    @property
    def is_unit(self) -> bool:
        """Check if has both task and modality not `None`."""

        return not (self.task is None or self.modality is None)

    def units(self) -> Generator["Scope", None, None]:
        """
        Generate each 'unit' subscopes of the current scope,
        i.e. subscope with specific task and modality

        Returns:
            Subscope with a task attribute.
        """

        if self.task is None:
            tasks = self.tasks()
        else:
            tasks = [self]
        for task in tasks:
            if task.modality is None:
                modalities = task.modalities()
            else:
                modalities = [task]
            for modality in modalities:
                yield modality

    def tasks(self) -> Generator["Scope", None, None]:
        """
        Generate subscopes of the current scope for each of its task.

        Returns:
            Subscope with a task attribute.
        """

        for task in self._tasks:
            if self._is_valid_subscope("task", task):
                model = getattr(self, task)
                yield model

    def modalities(self) -> Generator["Scope", None, None]:
        """
        Generate subscopes of the current scope for each of its modalities.

        Returns:
            Subscope with a modality attribute.
        """

        for modality in self._modalities:
            if self._is_valid_subscope("modality", modality):
                yield getattr(self, modality)

    def _set_step_collection(self):
        """Used in __init__(), set 'steps' attribute to an instance of step collection class"""

        if self.is_unit:
            step_collection_class = StepCollection
            return step_collection_class(self)

    def run(
        self,
        step_label: Optional[str] = None,
        force: Optional[bool] = False,
        debug: Optional[bool] = False,
    ):
        """Run all steps of the scope.
        
        Args:
            step_label: if not `None`, run only for the step with this label.
            force: Force run and overwrites result file(s) if already exist(s).
            debug: If False, log scripts errors and not raise them.
        """

        return self.dataset._run_manager.run(
            self, step_label=step_label, force=force, debug=debug
        )

    def status(self) -> pd.DataFrame:
        """
        Returns:
            Status for each step.
        """

        try:
            return pd.concat(
                [
                    unit.steps.status()
                    for unit in self.units()
                    if unit.steps.status() is not None
                ]
            )
        except ValueError:
            return pd.DataFrame()
