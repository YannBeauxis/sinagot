import pytest
import pandas as pd
from sinagot.utils import StepStatus, LOG_STEP_LABEL, LOG_STEP_STATUS


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

    rec = dataset.records.get("REC-200320-A").HDC.EEG
    step = rec.steps.get("preprocess")
    assert step.status() == StepStatus.PROCESSING
    step.run()
    assert step.status() == StepStatus.DONE


def test_steps_status(record):
    df_expected = unit_status_df(
        "REC-200319-A", "RS", "EEG", (("preprocess", 10), ("alpha", 0))
    )
    pd.testing.assert_frame_equal(record.EEG.RS.steps.status(), df_expected)
    df_expected = pd.concat(
        [
            unit_status_df(
                "REC-200319-A", "RS", "EEG", (("preprocess", 10), ("alpha", 0))
            ),
            unit_status_df("REC-200319-A", "MMN", "EEG", (("preprocess", 10),)),
            unit_status_df("REC-200319-A", "HDC", "EEG", (("preprocess", 10),)),
            unit_status_df(
                "REC-200319-A",
                "HDC",
                "behavior",
                (("scores", 30), ("scores_norm", 10)),
            ),
        ]
    ).reset_index()
    df_expected.pop("index")
    pd.testing.assert_frame_equal(record.steps.status(), df_expected)


def unit_status_df(record_id, task, modality, steps):
    return pd.DataFrame(
        [
            {
                "record_id": record_id,
                "task": task,
                "modality": modality,
                "step_index": index + 1,
                LOG_STEP_LABEL: label_value[0],
                LOG_STEP_STATUS: label_value[1],
            }
            for index, label_value in enumerate(steps)
        ]
    )
