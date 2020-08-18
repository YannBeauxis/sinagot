from sinagot import Workspace


def test_path_config_default_name(shared_datadir):
    paths = {
        "dataset_path": shared_datadir / "sonetaa" / "dataset",
        "scripts_path": shared_datadir / "sonetaa" / "scripts",
        "sonetaa_path": shared_datadir / "sonetaa",
    }
    for path in paths.values():
        ws = Workspace(path)
        assert ws._config_path == path / "workspace.toml"
        assert ws.data_path == paths["dataset_path"]
        assert ws._scripts_path == paths["scripts_path"]

    ws = Workspace(paths["sonetaa_path"], data_path=paths["scripts_path"])
    assert ws.data_path == paths["scripts_path"]
    ws = Workspace(str(paths["sonetaa_path"]))


def test_path_config_custom_name(shared_datadir):

    workspace_path = shared_datadir / "config_custom_name"
    config_path = workspace_path / "custom_name.toml"

    ws = Workspace(config_path)

    assert ws._config_path == config_path
    assert ws.data_path == workspace_path / "dataset"
    assert ws._scripts_path == workspace_path / "scripts"
