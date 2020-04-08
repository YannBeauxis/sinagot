import pytest
from sinagot import Dataset


def test_path(shared_datadir):
    paths = {
        "dataset_path": shared_datadir / "dataset",
        "scripts_path": shared_datadir / "scripts",
        "sonetaa_path": shared_datadir / "sonetaa",
    }
    for path in paths.values():
        ds = Dataset(path)
        assert ds._config_path == path
        assert ds._data_path == paths["dataset_path"]
        assert ds._scripts_path == paths["scripts_path"]

    ds = Dataset(paths["sonetaa_path"], data_path=paths["scripts_path"])
    assert ds._data_path == paths["scripts_path"]
    ds = Dataset(str(paths["sonetaa_path"]))
