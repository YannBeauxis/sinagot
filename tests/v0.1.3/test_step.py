import pytest
from sinagot.utils import StepStatus
from sinagot.models import Step
from sinagot.models.exceptions import NotFoundError, NoModalityError


def test_init_error(dataset):
    with pytest.raises(NoModalityError):
        Step("missing_label", dataset)
    with pytest.raises(NotFoundError):
        Step("missing_label", dataset.behavior)


def test_reload_script(dataset):

    STR_BEFORE = "test-before-modif"
    STR_AFTER = "test-after-modif"

    step = dataset.HDC.behavior.steps.first()
    assert step.script.test_modif() == STR_BEFORE

    script_path = dataset._scripts_path / "behavior" / "scores.py"
    script_path.write_text(script_path.read_text().replace(STR_BEFORE, STR_AFTER))

    step = dataset.HDC.behavior.steps.first()
    assert step.script.test_modif() == STR_AFTER


@pytest.mark.parametrize("dataset", [{"workspace": "multiple_path"}], indirect=True)
@pytest.mark.parametrize(
    "rec_id,status",
    [
        ("REC-000000-A", "DONE"),
        ("REC-000000-B", "DATA_READY"),
        ("REC-000000-C", "INIT"),
    ],
)
def test_script_multiple_path(dataset, rec_id, status):

    rec = dataset.get(rec_id)
    assert rec.base_task.base_mod.steps.first().status() == getattr(StepStatus, status)
