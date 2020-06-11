import pandas as pd


def test_record_count_detail(record):
    values = (
        ("RS", "EEG", 1),
        ("RS", "clinical", 1),
        ("MMN", "EEG", 1),
        ("MMN", "clinical", 1),
        ("HDC", "EEG", 1),
        ("HDC", "behavior", 0),
        ("HDC", "clinical", 1),
    )
    eval_dataframes(values, record.count_detail())


def test_dataset_count_detail(dataset):
    values = (
        ("HDC", "EEG", 2),
        ("HDC", "behavior", 1),
        ("HDC", "clinical", 2),
        ("MMN", "EEG", 2),
        ("MMN", "clinical", 2),
        ("RS", "EEG", 2),
        ("RS", "clinical", 2),
    )
    eval_dataframes(values, dataset.records.count_detail())


def gen_row(task, modality, count):
    return pd.DataFrame([{"task": task, "modality": modality, "count": count}])


def eval_dataframes(expected_values, target_dataframe):
    expected_df = (
        pd.concat([gen_row(*row) for row in expected_values])
        .reset_index()
        .sort_values(["task", "modality"])
    ).set_index(["task", "modality"])
    expected_df.pop("index")
    pd.testing.assert_frame_equal(
        expected_df, target_dataframe.sort_values(["task", "modality"])
    )
