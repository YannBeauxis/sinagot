import pandas as pd
import pytest

COUNT_VALUES = {
    "REC-200319-A": (
        ("RS", "EEG", 1),
        ("RS", "clinical", 1),
        ("MMN", "EEG", 1),
        ("MMN", "clinical", 1),
        ("HDC", "EEG", 1),
        ("HDC", "clinical", 1),
    ),
    "REC-200320-A": (
        ("RS", "EEG", 1),
        ("RS", "clinical", 1),
        ("MMN", "EEG", 1),
        ("MMN", "clinical", 1),
        ("HDC", "EEG", 1),
        ("HDC", "behavior", 1),
        ("HDC", "clinical", 1),
    ),
}

RECORD_PARAMS = "record_id,behavior", (("REC-200319-A", False), ("REC-200320-A", True))


@pytest.mark.parametrize(*RECORD_PARAMS)
def test_record_count_raw_data(workspace, record_id, behavior):
    COUNT_VALUES = [
        ("RS", "EEG", 1),
        ("RS", "clinical", 1),
        ("MMN", "EEG", 1),
        ("MMN", "clinical", 1),
        ("HDC", "EEG", 1),
        ("HDC", "clinical", 1),
    ]
    if behavior:
        COUNT_VALUES.append(("HDC", "behavior", 1))
    record = workspace.records.get(record_id)
    COLS = ["task", "modality", "count"]
    expected_df = pd.DataFrame(COUNT_VALUES, columns=COLS)
    expected_df.insert(0, "record_id", record.id)
    target_df = record.count_raw_data()
    eval_dataframes(expected_df, target_df, COLS)


@pytest.mark.parametrize(*RECORD_PARAMS)
def test_record_count_step(workspace, record_id, behavior):
    COUNT_VALUES = [
        ("RS", "clinical", 1),
        ("MMN", "clinical", 1),
        ("HDC", "clinical", 1),
    ]
    if behavior:
        COUNT_VALUES.append(("HDC", "behavior", 1))
    record = workspace.records.get(record_id)
    COLS = ["task", "modality", "count"]
    expected_df = pd.DataFrame(COUNT_VALUES, columns=COLS)
    expected_df.insert(0, "record_id", record_id)
    target_df = record.count_step(step_label="scores_norm", position="output")
    eval_dataframes(expected_df, target_df, COLS)


def test_dataset_count_raw_data(workspace):
    COUNT_VALUES = (
        ("RS", "EEG", 2),
        # ("RS", "clinical", 2),
        ("MMN", "EEG", 2),
        # ("MMN", "clinical", 2),
        ("HDC", "EEG", 2),
        # ("HDC", "clinical", 2),
        ("HDC", "behavior", 1),
    )
    COLS = ["task", "modality", "count"]
    expected_df = pd.DataFrame(COUNT_VALUES, columns=COLS)
    target_df = workspace.records.count_raw_data()
    eval_dataframes(expected_df, target_df, COLS)
    df_with_record_id = workspace.records.count_raw_data(with_record_id=True)
    assert "record_id" in df_with_record_id.columns


def test_dataset_count_step(workspace):
    COUNT_VALUES = [
        ("HDC", "behavior", 1),
    ]
    COLS = ["task", "modality", "count"]
    expected_df = pd.DataFrame(COUNT_VALUES, columns=COLS)
    target_df = workspace.records.count_step(
        step_label="scores_norm", position="output"
    )
    eval_dataframes(expected_df, target_df, COLS)


def eval_dataframes(expected_df, target_df, columns):
    expected_df = expected_df.sort_values(columns).reset_index(drop=True)
    target_df = target_df.sort_values(columns).reset_index(drop=True)
    pd.testing.assert_frame_equal(expected_df, target_df)
