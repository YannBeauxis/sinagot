"""Test scripts"""

from pathlib import Path


def test_path(workspace, ID):
    script = workspace.behavior.get(ID).steps.first().script
    assert script.path.input == Path(
        workspace.data_path, "HDC", ID, "Trial1_report.txt"
    )
    assert script.path.output == Path(
        workspace.data_path, "PROCESSED", ID, "HDC", "behavior-scores.csv"
    )


def test_create_output_dir(workspace):
    REC_ID = "REC-200606-A"
    record = workspace.RS.EEG.get(REC_ID)
    step = record.steps.get("alpha")
    script = step.script
    assert not all(script.data_exist.input.values())
    script.path.input.mkdir(parents=True)
    assert not script.path.output.parent.exists()
    step.run()
    assert script.path.output.parent.exists()
    for path in script._iter_paths("output"):
        assert not path.is_dir()
