# coding=utf-8

import pandas as pd
from sinagot.utils import get_plugin_modules
from sinagot.models import Record, RecordCollection


class SeriesRecord(Record):
    @property
    def series(self):
        collection_class = get_plugin_modules("pandas")["record_collection"]
        collection = collection_class(
            self.workspace, task=self.task, modality=self.modality
        )
        df = collection.dataframe
        if self.id in df.index:
            return df.loc[self.id]
        return pd.Series()

    def _unit_count_raw_data(self):
        if self.series is None:
            return 0
        return 1


class DataframeRecordCollection(RecordCollection):

    ID_FIELD = "record_id"
    DATE_FIELDS = ["date_of_birth", "date_of_recording"]

    _record_class = SeriesRecord
    is_unit = True

    @property
    def dataframe(self):
        sub_path = self.config["modalities"][self.modality]["models"]["dataframe_path"]
        file_path = self.workspace.data_path.joinpath(*sub_path)
        df = pd.read_csv(file_path, index_col="record_id", parse_dates=self.DATE_FIELDS)
        return df

    def iter_ids(self):
        """Return the list of all records ids in dataframe"""

        return list(self.dataframe.index)


MODELS = {"record": SeriesRecord, "record_collection": DataframeRecordCollection}
