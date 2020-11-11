import toml
import pytest
from sinagot import Workspace

MODES_WORKSPACES = [{"workspace": "minimal_mode"}, {"workspace": "sonetaa"}]


@pytest.fixture
def workspace(shared_datadir, request, change_run_mode):

    workspace = getattr(request, "param", {"workspace": "sonetaa"}).get(
        "workspace", "sonetaa"
    )

    # Change config to run mode
    run_mode = getattr(request, "param", None) and request.param.get("run_mode")
    if run_mode:
        config_path = shared_datadir / workspace / "workspace.toml"
        change_run_mode(config_path, run_mode)

    ws = Workspace(shared_datadir / workspace)
    yield ws
    ws.close()


@pytest.fixture
def custom_version_workspace(shared_datadir):
    class CustomWorkspace(Workspace):
        @property
        def version(self):
            return "0.2.0"

    return CustomWorkspace(shared_datadir / "sonetaa")


@pytest.fixture
def change_run_mode():
    def func(config_path, run_mode):
        config = toml.load(config_path)
        config["run"]["mode"] = run_mode
        config_path.write_text(toml.dumps(config))

    return func


@pytest.fixture
def TASKS():
    return ("RS", "MMN", "HDC")  # , "report")


@pytest.fixture
def IDS():
    return ("REC-200319-A", "REC-200320-A")


@pytest.fixture
def ID():
    return "REC-200319-A"


@pytest.fixture
def records(workspace, ID):
    return workspace.records


@pytest.fixture
def record(workspace, ID):
    return workspace.records.get(ID)
