from sinagot import Dataset


def test_path_config_default_name(shared_datadir):
    paths = {
        "dataset_path": shared_datadir / "sonetaa" / "dataset",
        "scripts_path": shared_datadir / "sonetaa" / "scripts",
        "sonetaa_path": shared_datadir / "sonetaa",
    }
    for path in paths.values():
        ds = Dataset(path)
        assert ds._config_path == path / "dataset.toml"
        assert ds._data_path == paths["dataset_path"]
        assert ds._scripts_path == paths["scripts_path"]

    ds = Dataset(paths["sonetaa_path"], data_path=paths["scripts_path"])
    assert ds._data_path == paths["scripts_path"]
    ds = Dataset(str(paths["sonetaa_path"]))

def test_path_config_custom_name(shared_datadir):

    workspace_path = shared_datadir / "config_custom_name" 
    config_path =  workspace_path / "custom_name.toml"

    ds = Dataset(config_path)

    assert ds._config_path == config_path
    assert ds._data_path == workspace_path / "dataset"
    assert ds._scripts_path == workspace_path / "scripts"
