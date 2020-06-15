import pandas as pd

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


def test_record_count_detail(record):
    COUNT_VALUES = (
        ("RS", "EEG", 1),
        ("RS", "clinical", 1),
        ("MMN", "EEG", 1),
        ("MMN", "clinical", 1),
        ("HDC", "EEG", 1),
        ("HDC", "clinical", 1),
        ("HDC", "behavior", 0),
    )
    COLS = ["task", "modality", "count"]
    expected_df = pd.DataFrame(COUNT_VALUES, columns=COLS)
    expected_df.insert(0, "record_id", record.id)
    target_df = record.count_detail()
    eval_dataframes(expected_df, target_df, COLS)


def test_dataset_count_detail(dataset):
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
    COLS = ["record_id", "task", "modality", "count"]
    values = [
        (rec_id, *vals) for rec_id, values in COUNT_VALUES.items() for vals in values
    ]
    expected_df = pd.DataFrame(values, columns=COLS)
    target_df = dataset.records.count_detail()
    eval_dataframes(expected_df, target_df, COLS)


def eval_dataframes(expected_df, target_df, columns):
    expected_df = expected_df.sort_values(columns).reset_index(drop=True)
    target_df = target_df.sort_values(columns).reset_index(drop=True)
    print(expected_df)
    print(target_df)
    pd.testing.assert_frame_equal(expected_df, target_df)
