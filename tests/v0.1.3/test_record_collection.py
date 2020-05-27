import re
import pytest
from sinagot.models import Record


def test_set_record_collection(dataset, shared_datadir):
    assert dataset.data_path == shared_datadir / "sonetaa" / "dataset"
    for task in ("RS", "MMN", "HDC"):
        task_record_collection = getattr(dataset, task)
        assert isinstance(task_record_collection, dataset._subscope_class)
        for modality in ("EEG", "clinical"):
            modality_record_collection = getattr(task_record_collection, modality)
            assert isinstance(modality_record_collection, dataset._subscope_class)


def test_modality_exists_only_for_the_right_tasks(dataset):
    hdc_behavior = dataset.HDC.behavior
    assert isinstance(hdc_behavior, dataset._subscope_class)
    with pytest.raises(AttributeError):
        assert dataset.EEG.behavior is None
    with pytest.raises(AttributeError):
        assert dataset.behavior.EEG is None


def test_custom_record_collection(dataset):
    assert dataset.EEG.__class__.__name__ == "RecordCollection"
    assert dataset.behavior.__class__.__name__ == "BehaviorSubset"
    assert dataset.behavior.test() == "Test !!"


def test_ids(dataset, IDS):
    assert set(dataset.ids()) == set(IDS)


def test_get(dataset, ID):
    rec = dataset.get(ID)
    assert isinstance(rec, Record)
    assert rec.id == ID


def test_first(dataset, IDS):
    rec = dataset.first()
    assert isinstance(rec, Record)
    assert rec.id in IDS


def test_all(dataset, IDS):
    ids = []
    for rec in dataset.all():
        assert isinstance(rec, Record)
        ids.append(rec.id)
        assert rec.id in IDS
    assert len(ids) == len(IDS)
    assert set(ids) == set(IDS)


def test_count(dataset, IDS):
    assert dataset.count() == len(IDS)


def test_has(dataset, ID):
    assert dataset.has(ID)
    assert not dataset.has("REC-010101-A")


def test_custom_record(dataset):
    CLASS_NAME = "BehaviorRecord"
    assert dataset.behavior._record_class.__name__ == CLASS_NAME
    rec = dataset.behavior.first()
    assert isinstance(rec, Record)
    assert rec.__class__.__name__ == CLASS_NAME
