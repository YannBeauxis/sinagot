# coding=utf-8

import pandas as pd
from sinagot.models import RecordCollection
from .record import ProcessedRecord


class ProcessedRecordCollection(RecordCollection):

    _record_class = ProcessedRecord

    def get_processed_data(self, **kwargs):
        return pd.concat([rec.get_processed_data(**kwargs) for rec in self.all()])
