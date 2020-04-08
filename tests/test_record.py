"""Test RecordCollection class"""
import pytest
from sinagot.models import Record


def test_set_subscope_record(record, TASKS):
    for task in TASKS:
        task_record = getattr(record, task)
        assert isinstance(task_record, record._subscope_class)
        assert task_record.task == task
        for modality in ("EEG", "clinical"):
            modality_subset = getattr(task_record, modality)
            assert modality_subset.modality == modality
            assert isinstance(modality_subset, record._subscope_class)

    #  Test modality exist only for the right tasks
    hdc_behavior = record.HDC.behavior
    assert isinstance(hdc_behavior, record._subscope_class)
    with pytest.raises(AttributeError):
        print(record.EEG.behavior)
        assert record.EEG.behavior is None
    with pytest.raises(AttributeError):
        assert record.behavior.EEG is None


def test_run(record):
    record.run()
