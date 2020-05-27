# coding=utf-8

from typing import Optional, Generator
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

    def iter_units(self) -> Generator["Scope", None, None]:
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

    #  TODO: Deprecated warning
    def units(self):
        """
        !!! warning 
            **DEPRECATED** Use `iter_units()` instead"""
        return self.iter_units()

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

    #  TODO: Deprecated warning
    def tasks(self):
        """
        !!! warning 
            **DEPRECATED** Use `iter_tasks()` instead"""
        return self.iter_tasks()

    def iter_modalities(self) -> Generator["Scope", None, None]:
        """
        Generate subscopes of the current scope for each of its modalities.

        Returns:
            Subscope with a modality attribute.
        """

        for modality in self._modalities:
            if self._is_valid_subscope("modality", modality):
                yield getattr(self, modality)

    #  TODO: Deprecated warning
    def modalities(self):
        """
        !!! warning 
            **DEPRECATED** Use `iter_modalities()` instead"""
        return self.iter_modalities()

    # TODO: deprecated warning
    def run(self, *args, **kwargs):
        """
        !!! warning 
            **DEPRECATED** Use `steps.run()` instead"""

        return self.steps.run(*args, **kwargs)

    # TODO: deprecated warning
    def status(self):
        """
        !!! warning 
            **DEPRECATED** Use `steps.status()` instead
        """

        return self.steps.status()
