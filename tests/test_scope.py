# coding=utf-8
from itertools import product


def test_tasks(records, record):
    SCOPES = (records, record)
    DIMENSIONS = (("tasks", "task", 3), ("modalities", "modality", 3))
    for scope, dimension in product(SCOPES, DIMENSIONS):
        method, label, number = dimension
        method = "iter_" + method
        assert not getattr(scope, label)
        childs = list(getattr(scope, method)())
        assert len(childs) == number
        for child in childs:
            assert isinstance(child, scope._subscope_class)
            assert getattr(child, label)
            assert len(list(getattr(child, method)())) == 0
