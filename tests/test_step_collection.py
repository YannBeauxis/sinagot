import pytest
from sinagot.models.exceptions import NoModalityError
from .conftest import MODES_WORKSPACES


@pytest.mark.parametrize(
    "dataset,names_class", zip(MODES_WORKSPACES, (list, dict)), indirect=["dataset"],
)
def test_step_scripts_names_shape(dataset, names_class):
    assert isinstance(dataset.records.steps.scripts_names(), names_class)


@pytest.mark.parametrize(
    "dataset", [{"workspace": "minimal_mode"}], indirect=True,
)
def test_minimal_mode(dataset):
    assert dataset.steps.scripts_names() == ["first_step", "next_step"]
    dataset.steps.run()


def test_scripts_name_scoped(dataset):
    assert dataset.HDC.behavior.steps.scripts_names() == ["scores", "scores_norm"]
    assert dataset.behavior.steps.scripts_names() == ["scores", "scores_norm"]
    assert dataset.HDC.EEG.steps.scripts_names() == ["preprocess"]
    assert dataset.RS.EEG.steps.scripts_names() == ["preprocess", "alpha"]
    assert dataset.steps
    assert dataset.steps.scripts_names() == {
        "behavior": ["scores", "scores_norm"],
        "EEG": ["preprocess", "alpha"],
        "clinical": [],
        "processed": [],
    }


def method_eval_label(dataset, method, *args):
    return {
        modality: getattr(step, "label", None)
        for modality, step in getattr(dataset.steps, method)(*args).items()
    }


@pytest.mark.parametrize(
    "dataset, label",
    zip(MODES_WORKSPACES, ("next_step", "scores")),
    indirect=["dataset"],
)
def test_get(dataset, label):
    if dataset.is_unit_mode:
        records = dataset
    else:
        records = dataset.HDC.behavior
        assert method_eval_label(dataset, "get", label) == {
            "behavior": "scores",
            "EEG": None,
            "clinical": None,
            "processed": None,
        }

    assert records.steps.get(label).label == label


@pytest.mark.parametrize(
    "dataset, label",
    zip(MODES_WORKSPACES, ("first_step", "scores")),
    indirect=["dataset"],
)
def test_first(dataset, label):
    if dataset.is_unit_mode:
        assert dataset.steps.first().label == label
    else:
        assert dataset.HDC.behavior.steps.first().label == label
        assert dataset.clinical.steps.first() == None
        assert method_eval_label(dataset, "first") == {
            "behavior": label,
            "EEG": "preprocess",
            "clinical": None,
            "processed": None,
        }


@pytest.mark.parametrize(
    "dataset", MODES_WORKSPACES, indirect=True,
)
def test_count(dataset):
    if dataset.is_unit_mode:
        dataset.steps.count() == 2
    else:
        assert dataset.HDC.behavior.steps.count() == 2
        assert dataset.clinical.steps.count() == 0
        assert dataset.steps.count() == {
            "behavior": 2,
            "EEG": 2,
            "clinical": 0,
            "processed": 0,
        }
        assert dataset.RS.steps.count() == {
            "EEG": 2,
            "clinical": 0,
        }
        assert dataset.MMN.steps.count() == {
            "EEG": 1,
            "clinical": 0,
        }
        assert dataset.HDC.steps.count() == {
            "behavior": 2,
            "EEG": 1,
            "clinical": 0,
        }
