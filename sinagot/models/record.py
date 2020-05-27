# coding=utf-8

import json
from collections import defaultdict
from typing import Optional
from io import StringIO
import pandas as pd
from sinagot.models import Scope
from sinagot.utils import (
    record_log_file_path,
    LOG_STEP_LABEL,
    LOG_STEP_STATUS,
)
from sinagot.models.exceptions import NotUnitError


class Record(Scope):
    """
    A Record instance is used to manipulate a single record data.
    It's accessed from a [RecordCollection](record_collection.md).
    
    Note:
        Inherite [Scope](scope.md) methods.

    Example:

    ```python
    rec = ds.get("RECORD-ID") # ds is a Dataset instance
    ```
    """

    _REPR_ATTRIBUTES = ["id", "task", "modality"]
    _MODEL_TYPE = "record"

    def __init__(self, dataset: "Dataset", record_id: str, *args, **kwargs):
        """
        Args:
            dataset: Root Dataset.
            record_id: ID of the record.
        """

        # TODO: raise exception if id not match regex in config
        self.id = record_id
        super().__init__(dataset, *args, **kwargs)

    def logs(self) -> pd.DataFrame:
        """
        Returns:
            Logs history.
        """

        log_path = record_log_file_path(self.dataset.data_path, self.id)
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

    # TODO: Test
    def count_detail(
        self, groupby: Optional[str] = None, group_mode: Optional[str] = "all"
    ) -> pd.DataFrame:
        """
        Args:
            groupby: If not `None`, columns to perform a groupby.
            group_mode: method to count the groupby. Possible values:

                - 'all': Return 1 if exists in all units of the aggregation, 0 if not.

                - 'any': Return 1 if exists in at least one unit.

                - 'mean': Return an mean for each unit.

        Returns:
            Detail count if record exists in each of tasks and modality.

        Raises:
            AttributeError: if group_mode not in ('all', 'any', 'mean').
        """

        if isinstance(groupby, str):
            groupby = [groupby]

        if group_mode not in ("all", "any", "mean"):
            raise AttributeError("aggregate_mode arg not valid")

        count = self._count_detail()
        if self.is_unit:
            count = pd.DataFrame([count])
        base = self._count_backbone()
        count = (
            base.merge(count, on=["task", "modality"])
            .eval("count = count_x + count_y")
            .reindex(["task", "modality", "count"], axis=1)
        )
        if groupby is not None:
            count = count.groupby(groupby)
            if group_mode == "all":
                count = count.min()
            if group_mode == "any":
                count = count.max()
            if group_mode == "mean":
                count = count.mean()
            return count.reset_index().reindex(groupby + ["count"], axis=1)
        return count

    def _count_detail(self):

        if self.is_unit:
            return pd.Series(
                {
                    "task": self.task,
                    "modality": self.modality,
                    "count": sum([self._unit_has_raw_data()]),
                }
            )
        else:
            return pd.DataFrame([unit._count_detail() for unit in self.iter_units()])

    def _unit_has_raw_data(self):
        if not self.is_unit:
            raise NotUnitError
        first_step = self.steps.first()
        if first_step:
            return first_step.script.data_exist.input
        return False

    def _count_backbone(self):
        """Used for count_detail() method."""

        return pd.DataFrame(
            [
                pd.Series({"task": task, "modality": modality, "count": 0})
                for task in self.config["tasks"]
                for modality in self.config["modalities"]
            ]
        )

    def status_json(self) -> str:
        """
        Returns:
            Status in JSON format for web API.
        """

        columns = ("step_index", LOG_STEP_LABEL, LOG_STEP_STATUS)

        return json.dumps(self._structure_status(columns))

    def _structure_status(self, columns):

        df = self.status()

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
