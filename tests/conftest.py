import toml
import pytest
from sinagot import Dataset


@pytest.fixture
def dataset(shared_datadir, request):

    # Change config to run mode
    run_mode = getattr(request, "param", None) and request.param.get("run_mode")
    print("run_mode", run_mode)
    if run_mode:
        config_path = shared_datadir / "sonetaa" / "dataset.toml"
        config = toml.load(config_path)
        config["run"]["mode"] = run_mode
        config_path.write_text(toml.dumps(config))

    return Dataset(shared_datadir / "sonetaa")


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
def record(dataset, ID):
    return dataset.get(ID)
