"""Test RecordCollection class"""
import pytest


def test_repr_scoped(record):
    for attr in ["task", "modality"]:
        assert attr in record.__str__()
        unit = record.RS.EEG
        assert unit.is_unit
        assert attr in unit.__str__()


@pytest.mark.parametrize("workspace", [{"workspace": "minimal_mode"}], indirect=True)
def test_repr_unit_mode(workspace):
    assert workspace.records.__class__.__name__ == "RecordCollection"
    record = workspace.records.first()
    assert record.__class__.__name__ == "Record"
    for attr in ["task", "modality"]:
        assert record.is_unit
        assert attr not in record.__str__()


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
