"""Test RecordCollection class"""
import pytest
from sinagot.models import Record


def test_set_subscope_record(record, TASKS):
    for task in TASKS:
        task_record = getattr(record, task)
        assert isinstance(task_record, record._subscope_class)
        assert task_record.task == task
        for modality in ("EEG", "clinical"):
            modality_record_collection = getattr(task_record, modality)
            assert modality_record_collection.modality == modality
            assert isinstance(modality_record_collection, record._subscope_class)


def test_modality_exist_only_for_the_right_tasks(record):
    hdc_behavior = record.HDC.behavior
    assert isinstance(hdc_behavior, record._subscope_class)
    with pytest.raises(AttributeError):
        assert record.EEG.behavior is None
    with pytest.raises(AttributeError):
        assert record.behavior.EEG is None


def test_run(record):
    record.steps.run()
