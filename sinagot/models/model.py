# coding=utf-8


class Model:
    """Base class for every model except scripts"""

    _REPR_ATTRIBUTES = []
    """List of instance attributes to display in __repr__"""
    workspace = None
    """Master workspace"""
    config = None
    """Config dic of the workspace"""
    logger = None
    """Logger object"""

    def __init__(self, workspace):
        self.workspace = workspace
        self.config = workspace.config
        self.logger = workspace.logger

    def __repr__(self):
        attributes = self._get_repr_attributes()
        if self._REPR_ATTRIBUTES:
            attributes = " | " + ", ".join(
                [
                    "{label}: {value}".format(label=label, value=getattr(self, label))
                    for label in self._get_repr_attributes()
                    if hasattr(self, label)
                ]
            )
        else:
            attributes = ""
        return "<{} instance{}>".format(self.__class__.__name__, attributes)

    @property
    def is_unit(self) -> bool:
        return True

    def _get_repr_attributes(self):
        return self._REPR_ATTRIBUTES
