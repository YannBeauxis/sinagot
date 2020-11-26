import re
import sinagot
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


def test_multiple_config_path(shared_datadir):
    conf_pathes = (
        shared_datadir / "sonetaa",
        shared_datadir / "sonetaa" / "custom_conf.toml",
    )
    ws = Workspace(conf_pathes[0])
    assert ws.config["run"]["mode"] == "dask"

    ws = Workspace(conf_pathes)
    assert ws.config["run"]["mode"] == "main_process"


def test_version_pattern():
    assert re.fullmatch(r"\d+\.\d+\.\d+", sinagot.__version__)


def test_default_workspace_version(workspace):
    assert workspace.version == "0.1.0"


def test_custom_workspace_version(shared_datadir, custom_version_workspace):
    assert custom_version_workspace.version == "0.2.0"
    conf_pathes = (
        shared_datadir / "sonetaa",
        shared_datadir / "sonetaa" / "custom_conf.toml",
    )
    ws = Workspace(conf_pathes)
    assert ws.version == "0.3.0"
