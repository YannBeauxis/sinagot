"""Test scripts"""

from pathlib import Path


def test_path(dataset, ID):
    script = dataset.behavior.get(ID).steps.first().script
    assert script.path.input == Path(dataset.data_path, "HDC", ID, "Trial1_report.txt")
    assert script.path.output == Path(
        dataset.data_path, "PROCESSED", ID, "HDC", "behavior-scores.csv"
    )


def test_create_output_dir(dataset):
    REC_ID = "REC-200606-A"
    record = dataset.RS.EEG.get(REC_ID)
    step = record.steps.get("alpha")
    script = step.script
    assert not script.data_exist.input
    script.path.input.mkdir(parents=True)
    assert not script.path.output.parent.exists()
    step.run()
    assert script.path.output.parent.exists()
    for path in script._iter_paths("output"):
        assert not path.is_dir()
