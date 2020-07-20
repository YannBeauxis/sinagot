import pytest


@pytest.mark.parametrize(
    "dataset", [{"run_mode": "main_process"}, {"run_mode": "dask"}], indirect=True
)
def test_log_only_record(dataset):
    dataset.steps.run()
    for record in dataset.records.all():
        ids = record.logs().record_id.unique()
        assert list(ids) == [record.id]
