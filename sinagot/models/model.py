# coding=utf-8

from pathlib import Path
from importlib import import_module, util as importutil


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
                for label in self._REPR_ATTRIBUTES
                if hasattr(self, label)
            ]
        )
        return "<{} instance | ".format(self.__class__.__name__) + attributes + ">"

    def _get_module(self, class_name, *args):
        """Import a module from scripts folder"""

        path = Path(self.dataset._scripts_path, *args)
        spec = importutil.spec_from_file_location(
            ".".join(args[-3:]), path.with_suffix(".py")
        )
        module = importutil.module_from_spec(spec)
        spec.loader.exec_module(module)
        return getattr(module, class_name)
