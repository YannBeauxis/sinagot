import toml
import pytest
from sinagot import Dataset

MODES_WORKSPACES = [{"workspace": "minimal_mode"}, {"workspace": "sonetaa"}]


@pytest.fixture
def dataset(shared_datadir, request):

    workspace = getattr(request, "param", {"workspace": "sonetaa"}).get(
        "workspace", "sonetaa"
    )

    # Change config to run mode
    run_mode = getattr(request, "param", None) and request.param.get("run_mode")
    if run_mode:
        config_path = shared_datadir / workspace / "dataset.toml"
        config = toml.load(config_path)
        config["run"]["mode"] = run_mode
        config_path.write_text(toml.dumps(config))

    return Dataset(shared_datadir / workspace)


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
def records(dataset, ID):
    return dataset.records


@pytest.fixture
def record(dataset, ID):
    return dataset.records.get(ID)
