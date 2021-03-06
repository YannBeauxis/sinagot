import pytest
from sinagot.utils import StepStatus
from sinagot.plugins.dask import DaskRunManager


@pytest.mark.parametrize(
    "workspace", [{"run_mode": "main_process"}, {"run_mode": "dask"}], indirect=True
)
def test_run_force(workspace):
    rec = workspace.behavior.get("REC-200320-A")
    out_path = rec.steps.get("scores_norm").script.path.output
    assert out_path.read_text() == "before force\n"
    rec.steps.run()
    assert out_path.read_text() == "before force\n"
    rec.steps.run(force=True)
    assert out_path.read_text() == "bla\n"
    workspace._run_manager.close()


@pytest.mark.parametrize(
    "workspace", [{"run_mode": "main_process"}, {"run_mode": "dask"}], indirect=True
)
def test_run_ignore_missing(workspace):
    rec = workspace.behavior.get("REC-200320-Z")
    out_path = rec.steps.get("scores_norm").script.path.output
    rec.steps.run()
    assert not out_path.exists()
    rec.steps.run(ignore_missing=True)
    assert out_path.exists()
    assert out_path.read_text() == "no input"


@pytest.mark.parametrize(
    "workspace", [{"run_mode": "main_process"}, {"run_mode": "dask"}], indirect=True
)
def test_run_step_label(workspace):
    rec = workspace.behavior.get("REC-200320-A")
    out_path = rec.steps.get("scores_norm").script.path.output
    assert out_path.read_text() == "before force\n"
    rec.steps.run("scores", force=True)
    assert out_path.read_text() == "before force\n"
    rec.steps.run(force=True)
    assert out_path.read_text() == "bla\n"
    workspace._run_manager.close()


@pytest.mark.parametrize(
    "workspace", [{"run_mode": "main_process"}, {"run_mode": "dask"}], indirect=True
)
def test_status_processing(workspace):

    rec = workspace.records.get("REC-200320-A").HDC.EEG
    step = rec.steps.get("preprocess")
    assert step.status() == StepStatus.PROCESSING
    rec.steps.run()
    assert step.status() == StepStatus.DONE


def test_record_collection_run(workspace):
    workspace.steps.run()
