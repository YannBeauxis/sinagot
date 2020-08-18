import pytest
from sinagot.models import StepCollectionUnit, StepCollection
from .conftest import MODES_WORKSPACES


@pytest.mark.parametrize(
    "workspace,is_unit_mode",
    zip(MODES_WORKSPACES, (True, False)),
    indirect=["workspace"],
)
def test_step_has_full_scope(workspace, is_unit_mode):
    assert workspace.is_unit_mode == is_unit_mode


@pytest.mark.parametrize(
    "workspace,steps_class",
    zip(MODES_WORKSPACES, (StepCollectionUnit, StepCollection)),
    indirect=["workspace"],
)
def test_step_collection_class(workspace, steps_class):
    assert isinstance(workspace.records.steps, steps_class)
