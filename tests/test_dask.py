import pytest
from sinagot import Dataset


def test_concurent_cluster(shared_datadir, change_run_mode, recwarn):
    config_path = shared_datadir / "sonetaa" / "dataset.toml"
    change_run_mode(config_path, "dask")
    ds1 = Dataset(config_path)
    ds2 = Dataset(config_path)
    print(recwarn[0])
    assert len(recwarn) == 0
