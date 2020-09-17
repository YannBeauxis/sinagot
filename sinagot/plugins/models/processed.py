# coding=utf-8

import pandas as pd
from sinagot.models import Record, RecordCollection


class ProcessedRecord(Record):

    _DATA_TYPES = {
        "str": str,
        "float": float,
        "int": int,
    }

    _CONFIG_PROCESSED_LABEL = "processed"
    _DATA_GETTER_LABEL = "data_getter"

    @classmethod
    def _data_getters(cls, getter_label):
        GETTERS = {
            "single_data": cls._get_single_data,
            "dataframe_from_csv": cls._get_dataframe_from_csv,
            "series_from_csv": cls._get_series_from_csv,
        }
        return GETTERS[getter_label]

    def get_processed_data(self, data_key):
        params = self.workspace.config[self._CONFIG_PROCESSED_LABEL][data_key]
        path = self._get_raw_path(params)
        if not path.exists():
            return pd.DataFrame(columns=params.get("columns"))
        getter_label = params.get(self._DATA_GETTER_LABEL, "single_data")
        getter = self._data_getters(getter_label)
        return getter(self, path, params).set_index("record_id")

    def _get_raw_path(self, params):
        record = Record(
            self.workspace,
            record_id=self.id,
            task=params["task"],
            modality=params["modality"],
        )
        step = record.steps.get(params["step_label"])
        path = step.script.path.output
        path_label = params.get("path_label")
        if path_label:
            path = path[path_label]
        return path

    def _get_single_data(self, path, params):

        data = path.read_text()
        data_type = params.get("data_type")
        if data_type:
            data = self._DATA_TYPES[data_type](data)
        return pd.DataFrame(
            [
                {
                    "record_id": self.id,
                    "task": params["task"],
                    "modality": params["modality"],
                    params["step_label"]: data,
                }
            ]
        )

    def _get_dataframe_from_csv(self, path, params=None):
        data = pd.read_csv(path)
        data = self._add_record_id_to_dataframe(data)
        return data

    def _get_series_from_csv(self, path, params=None):
        data = pd.read_csv(path, header=None, index_col=0).transpose()
        columns = params.get("columns")
        if columns:
            data = data.reindex(columns=columns)
        data = self._add_record_id_to_dataframe(data)
        return data

    def _add_record_id_to_dataframe(self, data):
        data.insert(0, "record_id", self.id)
        return data


class ProcessedRecordCollection(RecordCollection):

    _record_class = ProcessedRecord

    def get_processed_data(self, **kwargs):
        return pd.concat([rec.get_processed_data(**kwargs) for rec in self.all()])


MODELS = {"record": ProcessedRecord, "record_collection": ProcessedRecordCollection}
