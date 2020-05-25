def test_scripts_name(dataset):
    assert dataset.HDC.behavior.steps._scripts_names == ["scores", "scores_norm"]
    assert dataset.behavior.steps._scripts_names == ["scores", "scores_norm"]
    assert dataset.steps
    assert dataset.HDC.EEG.steps._scripts_names == ["preprocess"]
    assert dataset.RS.EEG.steps._scripts_names == ["preprocess", "alpha"]
