# coding=utf-8


class Model:
    """Base class for every model except scripts"""

    _REPR_ATTRIBUTES = []
    """List of instance attributes to display in __repr__"""
    dataset = None
    """Master dataset"""
    config = None
    """Config dic of the dataset"""
    logger = None
    """Logger object"""

    def __init__(self, dataset):
        self.dataset = dataset
        self.config = dataset.config
        self.logger = dataset.logger

    def __repr__(self):
        attributes = ", ".join(
            [
                "{label}: {value}".format(label=label, value=getattr(self, label))
                for label in self._get_repr_attributes()
                if hasattr(self, label)
            ]
        )
        return "<{} instance | ".format(self.__class__.__name__) + attributes + ">"

    @property
    def is_unit(self) -> bool:
        return True

    def _get_repr_attributes(self):
        return self._REPR_ATTRIBUTES
