# coding=utf-8

import json
from pathlib import Path
import pandas as pd
from sinagot.models import Scope, Record, RecordCollection


class PandasPath(Scope):
    @property
    def _data_raw_path(self):
        return self.config["modalities"][self.modality]["models"]["data_path"]


class PandasRecord(Record, PandasPath):
    def _get_data(self):
        data_path = Path(self._data_path)
        if data_path.exists():
            try:
                data = json.loads(data_path.read_text())
                data = pd.DataFrame().append(data, ignore_index=True)
                data.index = [self.id]
                return data.iloc[0]
            except Exception as ex:
                return None

    def _set_data(self, data):
        if isinstance(data, dict):
            data = pd.Series(data)
            print("data", data)
        if isinstance(data, pd.Series):
            data.T.to_json(self._data_path)

    data = property(_get_data, _set_data)

    @property
    def _data_path(self):
        data_path = self._data_raw_path
        data_path = Path(self.workspace.data_path).joinpath(*data_path)
        data_path = str(data_path).format(id=self.id)
        Path(data_path).parent.mkdir(exist_ok=True)
        return data_path

    def _unit_count_raw_data(self):
        if self.data is None:
            return 0
        return 1


class PandasRecordCollection(RecordCollection, PandasPath):

    ID_FIELD = "record_id"
    DATE_FIELDS = ["date_of_birth", "date_of_recording"]

    _record_class = PandasRecord
    is_unit = True

    @property
    def data(self):
        return pd.DataFrame({rec.id: rec.data for rec in self.all()}).T

    def _iter_path(self):
        return self._data_raw_path


MODELS = {"record": PandasRecord, "record_collection": PandasRecordCollection}
