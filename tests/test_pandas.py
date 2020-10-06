import pytest
import pandas as pd
from sinagot.plugins.models.pandas import PandasRecord, PandasRecordCollection


@pytest.fixture
def get_record_data(shared_datadir):
    def func(record_id):
        target_path = shared_datadir / "pandas" / "dataset" / record_id / "series.json"
        return pd.read_json(target_path, typ="series")

    return func


@pytest.mark.parametrize("workspace", [{"workspace": "pandas"}], indirect=True)
def test_get_data(workspace, record, get_record_data):
    assert isinstance(record.pandas, PandasRecord)
    data = record.pandas.data
    assert isinstance(data, pd.Series)
    assert data.age == 15
    assert data.iq == 105
    target = get_record_data(record.id)
    assert data.equals(target)


@pytest.mark.parametrize("workspace", [{"workspace": "pandas"}], indirect=True)
def test_set_data(workspace, record, get_record_data):
    NEW_AGE = 17
    origin = get_record_data(record.id)
    target = get_record_data(record.id)
    target.age = NEW_AGE
    record.pandas.data = target
    data = record.pandas.data
    assert data.age == NEW_AGE
    target = get_record_data(record.id)
    assert target.age == NEW_AGE
    assert data.equals(target)


@pytest.mark.parametrize("workspace", [{"workspace": "pandas"}], indirect=True)
def test_collection_all_records(workspace, records, IDS):
    assert isinstance(records.pandas, PandasRecordCollection)
    assert records.pandas.count() == len(IDS)


@pytest.mark.parametrize("workspace", [{"workspace": "pandas"}], indirect=True)
def test_collection_get_data(workspace, records):
    assert isinstance(records.pandas, PandasRecordCollection)
    data = records.pandas.data
    assert isinstance(data, pd.DataFrame)
    for rec in records.pandas.all():
        assert data.loc[rec.id].equals(rec.data)

