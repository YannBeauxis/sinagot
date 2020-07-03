
import pytest
from sinagot.utils import StepStatus
from sinagot.plugins.dask import DaskRunManager


@pytest.mark.parametrize(
    "dataset", [{"run_mode": "main_process"}, {"run_mode": "dask"}], indirect=True
)
def test_run_force(dataset):
    rec = dataset.behavior.get("REC-200320-A")
    out_path = rec.steps.get("scores_norm").script.path.output
    assert out_path.read_text() == "before force\n"
    rec.steps.run()
    assert out_path.read_text() == "before force\n"
    rec.steps.run(force=True)
    assert out_path.read_text() == "bla\n"
    dataset._run_manager.close()


@pytest.mark.parametrize(
    "dataset", [{"run_mode": "main_process"}, {"run_mode": "dask"}], indirect=True
)
def test_run_step_label(dataset):
    rec = dataset.behavior.get("REC-200320-A")
    out_path = rec.steps.get("scores_norm").script.path.output
    assert out_path.read_text() == "before force\n"
    rec.steps.run("scores", force=True)
    assert out_path.read_text() == "before force\n"
    rec.steps.run(force=True)
    assert out_path.read_text() == "bla\n"
    dataset._run_manager.close()


@pytest.mark.parametrize("dataset", [{"run_mode": "dask"}], indirect=True)
def test_dask(dataset):

    assert dataset.config["run"]["mode"] == "dask"
    assert isinstance(dataset._run_manager, DaskRunManager)
    rec = dataset.records.get("REC-200320-A").HDC.EEG
    step = rec.steps.get("preprocess")
    assert step.status() == StepStatus.PROCESSING
    # TODO: Handle asyncio
    rec.steps.run()
    assert step.status() == StepStatus.DONE
    dataset._run_manager.close()


def test_record_collection_run(dataset):
    dataset.steps.run()
