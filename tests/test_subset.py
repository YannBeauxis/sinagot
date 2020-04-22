import re
import pytest
from sinagot.models import Record


def test_set_subset(dataset, shared_datadir):
    ds = dataset
    assert ds._data_path == shared_datadir / "sonetaa" / "dataset"
    for task in ("RS", "MMN", "HDC"):
        task_subset = getattr(ds, task)
        assert isinstance(task_subset, ds._subscope_class)
        for modality in ("EEG", "clinical"):
            modality_subset = getattr(task_subset, modality)
            assert isinstance(modality_subset, ds._subscope_class)

    #  Test modality exist only for the right tasks
    hdc_behavior = ds.HDC.behavior
    assert isinstance(hdc_behavior, ds._subscope_class)
    with pytest.raises(AttributeError):
        assert ds.EEG.behavior is None
    with pytest.raises(AttributeError):
        assert ds.behavior.EEG is None


def test_custom_subset(dataset):
    assert dataset.EEG.__class__.__name__ == "Subset"
    assert dataset.behavior.__class__.__name__ == "BehaviorSubset"
    assert dataset.behavior.test() == "Test !!"


def test_run(dataset):
    dataset.run()


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
