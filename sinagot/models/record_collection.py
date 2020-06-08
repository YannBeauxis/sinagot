# coding=utf-8

from typing import Optional
from pathlib import Path
import re
from typing import Generator
import pandas as pd
from sinagot.models import Scope, Record


class RecordCollection(Scope):
    """
    A RecordCollection is used to manipulate a collection of [Record](record.md).

    Note:
        Inherite [Scope](scope.md) methods.

    Example:

    ```python
    # access record_collection of all EEG records (EEG is a task)
    sub = ds.EEG  # ds is a Dataset instance
    ```
    """

    _MODEL_TYPE = "record_collection"
    _record_class = Record

    def __init__(self, *args, **kwargs):
        self._subscope_class = self.__class__
        super().__init__(*args, **kwargs)
        modality = self.modality
        # Check for custom record class
        if modality is not None:
            try:
                class_name = self.config["modalities"][modality]["models"]["record"]
                self._record_class = self._get_module(
                    class_name, modality, "models", "record"
                )
            except KeyError:
                pass
        self._ids = []

    #  TODO: Deprecated warning
    def ids(self):
        """
        !!! warning 
            **DEPRECATED** Use `iter_ids()` instead"""
        return self.iter_ids()

    def iter_ids(self) -> Generator[str, None, None]:
        """Generator all record ids within the record_collection.
        
        Returns:
            Record ID.
        """
        # TODO: use dataset cache for ids
        if self.is_unit:
            for record_id in self._iter_ids_unit():
                yield record_id
        else:
            units = self.iter_units()
            self._ids = []
            for unit in units:
                for record_id in unit.iter_ids():
                    if self._is_new_id(record_id):
                        yield record_id

    def _is_new_id(self, record_id):
        ids = self._ids
        if record_id in ids:
            return False
        ids.append(record_id)
        self._ids = ids
        return True

    def _iter_ids_unit(self):
        """Return the list of all records ids i.e. subfolder names"""
        self._ids = []

        first_script = self.steps.first()

        if first_script:
            path_raw = first_script.script.PATH_IN
            if isinstance(path_raw, dict):
                path_tuple = path_raw.values()[0]
            else:
                path_tuple = path_raw

            root_path = Path(self.dataset.data_path)
            raw_pattern = Path(*path_tuple)
            glob_pattern = str(self._glob_pattern(raw_pattern))
            re_pattern = re.compile(str(root_path / self._re_pattern(raw_pattern)))

            for path in root_path.glob(glob_pattern):
                record_id = self._evaluate_path(re_pattern, path)
                if record_id:
                    yield record_id

    def _evaluate_path(self, re_pattern, path):
        m = re_pattern.search(str(path))
        if m and (len(m.groups()) > 0):
            record_id = m.group(1)
            if self._is_new_id(record_id):
                return record_id

    def _glob_pattern(self, raw_pattern):
        return str(raw_pattern).format(id="*", task="*",)

    def _re_pattern(self, raw_pattern):
        return str(raw_pattern).format(
            id="({})".format(self.config["records"]["id_pattern"]),
            task="(?:{})".format(self.task),
        )

    def all(self) -> Generator["Record", None, None]:
        """Generate all records instances of the record_collection.
        
        Returns:
            sinagot.models.Record: Record instance
        """

        for record_id in self.iter_ids():
            yield self.get(record_id)

    def first(self) -> "Record":
        """
        Get the first record found.
        
        Returns:
            Record instance
        """

        for record_id in self.iter_ids():
            return self.get(record_id)

    def get(self, record_id: str) -> "Record":
        """
        Get record by ID.

        Args:
            record_id: record ID

        Returns:
            Record instance
        """

        return self._record_class(
            dataset=self.dataset,
            record_id=record_id,
            task=self.task,
            modality=self.modality,
        )

    def has(self, record_id: str) -> bool:
        """
        Check existance of a record in the record_collection.
        
        Args:
            record_id: Id of the record.
        
        Returns:
            True if record exists.
        """

        for id_ in self.iter_ids():
            if id_ == record_id:
                return True
        return False

    def count(self) -> int:
        """
        Count all records.

        Returns:
            Number of records.
        """

        return sum(1 for rec in self.iter_ids())

    def _count_detail_unit(self):

        return pd.DataFrame(
            [
                {
                    "record_id": record_id,
                    "task": self.task,
                    "modality": self.modality,
                    "count": 1,
                }
                for record_id in self.iter_ids()
            ]
        )

    # TODO: To test
    def logs(self) -> pd.DataFrame:
        """
        Returns:
            Logs history.
        """
        return pd.concat([rec.logs() for rec in self.all()])
