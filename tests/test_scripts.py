"""Test scripts"""

from pathlib import Path


def test_path(dataset, ID):
    script = dataset.behavior.get(ID).steps.first().script
    assert script.path.input == Path(dataset.data_path, "HDC", ID, "Trial1_report.txt")
    assert script.path.output == Path(
        dataset.data_path, "PROCESSED", ID, "HDC", "behavior-scores.csv"
    )
