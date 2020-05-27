import pytest
from sinagot.models.exceptions import NoModalityError


def test_scripts_name(dataset):
    assert dataset.HDC.behavior.steps._scripts_names() == ["scores", "scores_norm"]
    assert dataset.behavior.steps._scripts_names() == ["scores", "scores_norm"]
    assert dataset.HDC.EEG.steps._scripts_names() == ["preprocess"]
    assert dataset.RS.EEG.steps._scripts_names() == ["preprocess", "alpha"]
    assert dataset.steps
    assert dataset.steps._scripts_names() == {
        "behavior": ["scores", "scores_norm"],
        "EEG": ["preprocess", "alpha"],
        "clinical": [],
    }


def test_non_modality_methods_exception(dataset):
    with pytest.raises(NoModalityError):
        dataset.steps._modality_get("some_label")


def method_eval_label(dataset, method, *args):
    return {
        modality: getattr(step, "label", None)
        for modality, step in getattr(dataset.steps, method)(*args).items()
    }


def test_get(dataset):
    label = "scores"
    assert dataset.HDC.behavior.steps.get(label).label == label
    assert method_eval_label(dataset, "get", label) == {
        "behavior": "scores",
        "EEG": None,
        "clinical": None,
    }


def test_first(dataset):
    assert dataset.HDC.behavior.steps.first().label == "scores"
    assert dataset.clinical.steps.first() == None
    assert method_eval_label(dataset, "first") == {
        "behavior": "scores",
        "EEG": "preprocess",
        "clinical": None,
    }


def test_count(dataset):
    assert dataset.HDC.behavior.steps.count() == 2
    assert dataset.clinical.steps.count() == 0
    assert dataset.steps.count() == {
        "behavior": 2,
        "EEG": 2,
        "clinical": 0,
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
