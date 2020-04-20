import pytest
from sinagot.utils import StepStatus


@pytest.mark.parametrize(
    "dataset", [{"run_mode": "main_process"}, {"run_mode": "dask"}], indirect=True
)
def test_step_status(dataset, record):

    rec = record.HDC.behavior
    step = rec.steps.get("scores")
    assert step.status() == StepStatus.DONE
    step = rec.steps.get("scores_norm")
    assert step.status() == StepStatus.DATA_READY
    step.run()
    assert step.status() == StepStatus.DONE

    rec = dataset.get("REC-200320-A").HDC.EEG
    step = rec.steps.get("preprocess")
    assert step.status() == StepStatus.PROCESSING
    step.run()
    assert step.status() == StepStatus.DONE
