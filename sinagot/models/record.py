# coding=utf-8

import json
from collections import defaultdict
from io import StringIO
import json_lines
import pandas as pd
from sinagot.models import ModelWithStepCollection, Scope
from sinagot.utils import (
    record_log_file_path,
    LOG_STEP_LABEL,
    LOG_STEP_STATUS,
)
from sinagot.models.exceptions import NotUnitError


class RecordUnit(ModelWithStepCollection):

    _REPR_ATTRIBUTES = ["id"]
    _MODEL_TYPE = "record"

    def __init__(self, workspace: "Workspace", record_id: str, *args, **kwargs):
        """
        Args:
            workspace: Root Workspace.
            record_id: ID of the record.
        """

        # TODO: raise exception if id not match regex in config
        self.id = record_id
        super().__init__(workspace, *args, **kwargs)
        self.steps: "StepCollection" = self.set_step_collection()
        """Collection of steps."""

    def _structure_status(self, columns):

        df = self.steps.status()

        def status_default_dict():
            def dict_to_list():
                return defaultdict(list)

            return defaultdict(dict_to_list)

        def get_status_dict(df):
            sd = status_default_dict()
            for row in df.itertuples():
                sd[row.task][row.modality].append(
                    {key: getattr(row, key) for key in columns}
                )
            return sd

        return get_status_dict(df)


class Record(RecordUnit, Scope):
    """
    A Record instance is used to manipulate a single record data.
    It's accessed from a [RecordCollection](record_collection.md).
    
    Note:
        Inherite [Scope](scope.md) methods.

    Example:

    ```python
    rec = ws.get("RECORD-ID") # ws is a Workspace instance
    ```
    """

    @property
    def _log_path(self):
        return record_log_file_path(self.workspace.data_path, self.id)

    def logs_json(self):
        log_path = self._log_path
        with open(log_path, "rb") as file_object:
            data = json_lines.reader(file_object)
            return list(data)

    def logs(self) -> pd.DataFrame:
        """
        Returns:
            Logs history.
        """

        log_path = self._log_path
        if log_path.exists():
            json = "[{}]".format(",".join(log_path.read_text().split("\n")[:-1]))
            df = pd.read_json(StringIO(json), orient="records")
            for key in ("task", "modality"):
                k = getattr(self, key)
                if k is not None:
                    df = df.query("{} == '{}'".format(key, k))
            return df.sort_values("time", ascending=False)
        else:
            return pd.DataFrame()

    def _count_detail_unit(self):

        return pd.DataFrame(
            [
                {
                    "record_id": self.id,
                    "task": self.task,
                    "modality": self.modality,
                    "count": self._unit_count_raw_data(),
                }
            ]
        )

    def _unit_count_raw_data(self):
        if not self.is_unit:
            raise NotUnitError
        first_step = self.steps.first()
        if first_step and first_step.script.data_exist.input:
            return 1
        return 0

    def status_dict(self) -> str:
        """
        Returns:
            Status in dict format.
        """

        columns = ("step_index", LOG_STEP_LABEL, LOG_STEP_STATUS)

        return self._structure_status(columns)

    def status_json(self) -> str:
        """
        Returns:
            Status in JSON format for web API.
        """

        return json.dumps(self.status_dict())
