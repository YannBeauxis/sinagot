import pytest
from sinagot.models import StepCollectionUnit, StepCollection
from .conftest import MODES_WORKSPACES


@pytest.mark.parametrize(
    "dataset,is_unit_mode", zip(MODES_WORKSPACES, (True, False)), indirect=["dataset"]
)
def test_step_has_full_scope(dataset, is_unit_mode):
    assert dataset.is_unit_mode == is_unit_mode


@pytest.mark.parametrize(
    "dataset,steps_class",
    zip(MODES_WORKSPACES, (StepCollectionUnit, StepCollection)),
    indirect=["dataset"],
)
def test_step_collection_class(dataset, steps_class):
    assert isinstance(dataset.records.steps, steps_class)
