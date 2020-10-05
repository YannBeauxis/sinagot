# coding=utf-8
from itertools import product
import pytest


def test_tasks(records, record):
    SCOPES = (records, record)
    DIMENSIONS = (("tasks", "task", 3), ("modalities", "modality", 4))
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


@pytest.mark.parametrize(
    "task,modality,class_names",
    [
        (None, None, ("RecordCollection", "Record")),
        ("RS", None, ("RecordCollection", "Record")),
        ("HDC", None, ("RecordCollection", "Record")),
        ("MMN", None, ("RecordCollection", "Record")),
        (None, "EEG", ("RecordCollection", "Record")),
        (None, "clinical", ("PandasRecordCollection", "PandasRecord")),
        (None, "processed", ("ProcessedRecordCollection", "ProcessedRecord")),
        ("RS", "EEG", ("RecordCollection", "Record")),
        ("HDC", "behavior", ("BehaviorRecordCollection", "BehaviorRecord")),
        ("MMN", "clinical", ("PandasRecordCollection", "PandasRecord")),
    ],
)
def test_get_subscope(records, record, task, modality, class_names):
    for parent, class_name in zip((records, record), class_names):
        scope = parent.get_subscope(task=task, modality=modality)
        assert scope.task == task
        assert scope.modality == modality
        assert scope.__class__.__name__ == class_name
