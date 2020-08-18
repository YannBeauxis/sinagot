import pytest
from sinagot.models import Record


def test_set_record_collection(workspace, records, shared_datadir):
    assert workspace.data_path == shared_datadir / "sonetaa" / "dataset"
    for task in ("RS", "MMN", "HDC"):
        task_record_collection = getattr(records, task)
        assert isinstance(task_record_collection, records._subscope_class)
        for modality in ("EEG", "clinical"):
            modality_record_collection = getattr(task_record_collection, modality)
            assert isinstance(modality_record_collection, records._subscope_class)


def test_modality_exists_only_for_the_right_tasks(records):
    hdc_behavior = records.HDC.behavior
    assert isinstance(hdc_behavior, records._subscope_class)
    with pytest.raises(AttributeError):
        assert records.EEG.behavior is None
    with pytest.raises(AttributeError):
        assert records.behavior.EEG is None


def test_custom_record_collection(records):
    assert records.EEG.__class__.__name__ == "RecordCollection"
    assert records.behavior.__class__.__name__ == "BehaviorRecordCollection"
    assert records.behavior.test() == "Test !!"


def test_ids(records, IDS):
    assert set(records.iter_ids()) == set(IDS)


def test_get(records, ID):
    rec = records.get(ID)
    assert isinstance(rec, Record)
    assert rec.id == ID


def test_first(records, IDS):
    rec = records.first()
    assert isinstance(rec, Record)
    assert rec.id in IDS


def test_all(records, IDS):
    ids = []
    for rec in records.all():
        assert isinstance(rec, Record)
        ids.append(rec.id)
        assert rec.id in IDS
    assert len(ids) == len(IDS)
    assert set(ids) == set(IDS)


def test_count(records, IDS):
    assert records.count() == len(IDS)


def test_has(records, ID):
    assert records.has(ID)
    assert not records.has("REC-010101-A")


def test_custom_record(records):
    CLASS_NAME = "BehaviorRecord"
    assert records.behavior._record_class.__name__ == CLASS_NAME
    rec = records.behavior.first()
    assert isinstance(rec, Record)
    assert rec.__class__.__name__ == CLASS_NAME
