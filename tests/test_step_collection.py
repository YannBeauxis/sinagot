import pytest
from sinagot.models.exceptions import NoModalityError
from .conftest import MODES_WORKSPACES


@pytest.mark.parametrize(
    "workspace,names_class",
    zip(MODES_WORKSPACES, (list, dict)),
    indirect=["workspace"],
)
def test_step_scripts_names_shape(workspace, names_class):
    assert isinstance(workspace.records.steps.scripts_names(), names_class)


@pytest.mark.parametrize(
    "workspace", [{"workspace": "minimal_mode"}], indirect=True,
)
def test_minimal_mode(workspace):
    assert workspace.steps.scripts_names() == ["first_step", "next_step"]
    workspace.steps.run()


def test_scripts_name_scoped(workspace):
    assert workspace.HDC.behavior.steps.scripts_names() == ["scores", "scores_norm"]
    assert workspace.behavior.steps.scripts_names() == ["scores", "scores_norm"]
    assert workspace.HDC.EEG.steps.scripts_names() == ["preprocess"]
    assert workspace.RS.EEG.steps.scripts_names() == ["preprocess", "alpha"]
    assert workspace.steps
    assert workspace.steps.scripts_names() == {
        "behavior": ["scores", "scores_norm"],
        "EEG": ["preprocess", "alpha"],
        "clinical": [],
        "processed": [],
    }


def method_eval_label(workspace, method, *args):
    return {
        modality: getattr(step, "label", None)
        for modality, step in getattr(workspace.steps, method)(*args).items()
    }


@pytest.mark.parametrize(
    "workspace, label",
    zip(MODES_WORKSPACES, ("next_step", "scores")),
    indirect=["workspace"],
)
def test_get(workspace, label):
    if workspace.is_unit_mode:
        records = workspace
    else:
        records = workspace.HDC.behavior
        assert method_eval_label(workspace, "get", label) == {
            "behavior": "scores",
            "EEG": None,
            "clinical": None,
            "processed": None,
        }

    assert records.steps.get(label).label == label


@pytest.mark.parametrize(
    "workspace, label",
    zip(MODES_WORKSPACES, ("first_step", "scores")),
    indirect=["workspace"],
)
def test_first(workspace, label):
    if workspace.is_unit_mode:
        assert workspace.steps.first().label == label
    else:
        assert workspace.HDC.behavior.steps.first().label == label
        assert workspace.clinical.steps.first() == None
        assert method_eval_label(workspace, "first") == {
            "behavior": label,
            "EEG": "preprocess",
            "clinical": None,
            "processed": None,
        }


@pytest.mark.parametrize(
    "workspace", MODES_WORKSPACES, indirect=True,
)
def test_count(workspace):
    if workspace.is_unit_mode:
        workspace.steps.count() == 2
    else:
        assert workspace.HDC.behavior.steps.count() == 2
        assert workspace.clinical.steps.count() == 0
        assert workspace.steps.count() == {
            "behavior": 2,
            "EEG": 2,
            "clinical": 0,
            "processed": 0,
        }
        assert workspace.RS.steps.count() == {
            "EEG": 2,
            "clinical": 0,
        }
        assert workspace.MMN.steps.count() == {
            "EEG": 1,
            "clinical": 0,
        }
        assert workspace.HDC.steps.count() == {
            "behavior": 2,
            "EEG": 1,
            "clinical": 0,
        }
