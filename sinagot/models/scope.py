# coding=utf-8

from importlib import import_module
from typing import Optional, Generator
import pandas as pd
from sinagot.models import Model, StepCollection


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
            self.task: Optional[str] = task
            """Task of the scope. If `None`, the scope represents all available tasks."""
        if modality is not None:
            self.modality: Optional[str] = modality
            """Modality of the scope. If `None`, the scope represents all available modalities."""
        if self._subscope_class is None:
            self._subscope_class = self.__class__
        super().__init__(dataset)

        self.steps: StepCollection = StepCollection(self)
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
        subscope_access = property(
            cls._property_factory(_subscope_class, subscope, value)
        )
        setattr(
            cls, value, subscope_access,
        )
        return value

    @classmethod
    def _search_custom_subscope_in_config(cls, subscope, value, dataset):
        model_type = cls._MODEL_TYPE
        if subscope == "modality":

            sub_config = dataset.config
            for key in ("modalities", value, "models"):
                sub_config = sub_config.get(key, {})

            custom_class = cls._get_custom_class(dataset, value)
            if custom_class:
                return custom_class

            plugin_model = sub_config.get("plugin")
            if plugin_model:
                return cls._get_plugin_modules(plugin_model)[model_type]
        return cls

    @classmethod
    def _get_custom_class(cls, dataset, value):
        model_type = cls._MODEL_TYPE
        base_class_name = model_type.title().replace("_", "")
        try:
            custom_class = dataset._get_module(
                base_class_name, value, "models", model_type
            )
        except FileNotFoundError:
            return None
        custom_class.__name__ = value.title() + base_class_name
        if model_type == "record_collection":
            record_class = custom_class._record_class._get_custom_class(dataset, value)
            if record_class:
                custom_class._record_class = record_class
        return custom_class

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

    # TODO: To test
    def count_group(
        self, groupby: Optional[str] = None, group_mode: Optional[str] = "all",
    ) -> pd.DataFrame:
        """
        Args:
            groupby: If not `None`, columns to perform a groupby.
            group_mode: method to count the groupby. Possible values:

                - 'all': Sum if exists in each scope of the aggregation.

                - 'any': Sum if exists in at least one scope of the aggregation.

                - 'mean': Mean each scope of the aggregation.

        Returns:
            Detail count if record exists i.e. has raw data.

        Raises:
            AttributeError: if group_mode not in ('all', 'any', 'mean').
        """

        if isinstance(groupby, str):
            groupby = [groupby]

        if group_mode not in ("all", "any", "mean"):
            raise AttributeError("aggregate_mode arg not valid")

        count = self.count_detail()
        count = count.groupby(["task", "modality"]).sum()
        if groupby:
            count = count.groupby(groupby)
            if group_mode == "all":
                count = count.min()
            if group_mode == "any":
                count = count.max()
            if group_mode == "mean":
                count = count.mean()
            return count.reset_index().reindex(groupby + ["count"], axis=1)
        return count

    def count_detail(self):

        if self.is_unit:
            df = self._count_detail_unit()
        else:
            df = pd.concat([unit.count_detail() for unit in self.iter_units()])
        df.reset_index(drop=True, inplace=True)
        return df

    def _count_detail_unit(self):
        return pd.DataFrame()
