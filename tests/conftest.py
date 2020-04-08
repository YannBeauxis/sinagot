import pytest
from sinagot import Dataset


@pytest.fixture
def dataset(shared_datadir):
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
