class NotUnitError(Exception):
    """Rise when a model is not a unit"""


class NoModalityError(Exception):
    """Rise when a model has no specific modality"""


class NotFoundError(Exception):
    """Rise when finding method return nothing"""
