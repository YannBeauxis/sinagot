import pytest
from sinagot.models import StepCollection, ScopedStepCollection
from .conftest import MODES_WORKSPACES


@pytest.mark.parametrize(
    "dataset,is_unit", zip(MODES_WORKSPACES, (True, False)), indirect=["dataset"]
)
def test_step_has_full_scope(dataset, is_unit):
    assert dataset.is_unit == is_unit


@pytest.mark.parametrize(
    "dataset,steps_class",
    zip(MODES_WORKSPACES, (StepCollection, ScopedStepCollection)),
    indirect=["dataset"],
)
def test_step_collection_class(dataset, steps_class):
    assert isinstance(dataset.records.steps, steps_class)
