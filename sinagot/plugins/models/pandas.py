# coding=utf-8

from pathlib import Path
import pandas as pd
from sinagot.utils import get_plugin_modules
from sinagot.models import Scope, Record, RecordCollection


class PandasPath(Scope):
    @property
    def _data_raw_path(self):
        return self.config["modalities"][self.modality]["models"]["data_path"]


class PandasRecord(Record, PandasPath):
    def _get_data(self):
        if Path(self._data_path).exists():
            try:
                data = pd.read_csv(self._data_path, index_col=0, header=None)
                return data.T.iloc[0]
            except:
                return None

    def _set_data(self, data):
        if isinstance(data, dict):
            data = pd.Series(data)
            print("data", data)
        if isinstance(data, pd.Series):
            data.T.to_csv(self._data_path, header=None)

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
        # sub_path = self.config["modalities"][self.modality]["models"]["dataframe_path"]
        # file_path = self.workspace.data_path.joinpath(*sub_path)
        # df = pd.read_csv(file_path, index_col="record_id", parse_dates=self.DATE_FIELDS)
        # return df

    def _iter_path(self):
        return self._data_raw_path

    # def iter_ids(self):
    #     """Return the list of all records ids in dataframe"""

    #     return list(self.dataframe.index)


MODELS = {"record": PandasRecord, "record_collection": PandasRecordCollection}
