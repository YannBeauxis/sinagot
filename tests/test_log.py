import pytest


@pytest.mark.parametrize(
    "workspace", [{"run_mode": "main_process"}, {"run_mode": "dask"}], indirect=True
)
def test_log_only_record(workspace):
    workspace.steps.run()
    for record in workspace.records.all():
        ids = record.logs().record_id.unique()
        assert list(ids) == [record.id]
