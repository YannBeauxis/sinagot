# coding=utf-8

from typing import Generator
import pandas as pd
from sinagot.utils import get_module, PathExplorer
from sinagot.models import ModelWithStepCollection, Scope, Record, RecordUnit


class RecordCollectionUnit(ModelWithStepCollection):

    _MODEL_TYPE = "record_collection"
    _record_class = RecordUnit
    task = None

    def ids(self) -> list:
        """List of all records ids
    
        Returns:
            Record ids"""
        return list(self.iter_ids())

    def iter_ids(self):
        """Generator all record ids within the record_collection.
        
        Returns:
            Record ID.
        """

        path_raw = self._iter_path()

        if path_raw:
            path_expl = PathExplorer(self, path_raw)
            return path_expl.iter_ids()

    def _iter_path(self):
        first_script = self.steps.first()
        if first_script:
            return first_script.script.PATH_IN

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

    def head(self, count=5) -> "Record":
        """
        Get the first record found.
        
        Returns:
            Record instance
        """

        idx = 0
        for record_id in self.iter_ids():
            yield self.get(record_id)
            idx += 1
            if idx > count:
                break

    def get(self, record_id: str) -> "Record":
        """
        Get record by ID.

        Args:
            record_id: record ID

        Returns:
            Record instance
        """

        return self._record_class(workspace=self.workspace, record_id=record_id,)

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


class RecordCollection(RecordCollectionUnit, Scope):
    """
    A RecordCollection is used to manipulate a collection of [Record](record.md).

    Note:
        Inherite [Scope](scope.md) methods.

    Example:

    ```python
    # access record_collection of all EEG records (EEG is a task)
    sub = ws.EEG  # ws is a Workspace instance
    ```
    """

    _record_class = Record

    def __init__(self, *args, **kwargs):
        self._subscope_class = self.__class__
        super().__init__(*args, **kwargs)
        modality = self.modality
        # Check for custom record class
        if modality is not None:
            try:
                class_name = self.config["modalities"][modality]["models"]["record"]
                self._record_class = get_module(
                    self.workspace, class_name, modality, "models", "record"
                )
            except KeyError:
                pass
        self._ids = []

    def iter_ids(self) -> Generator[str, None, None]:
        """Generator all record ids within the record_collection.

        Returns:
            Record ID.
        """
        # TODO: use workspace cache for ids
        if self.is_unit:
            for record_id in super().iter_ids():
                yield record_id
        else:
            ids = []
            for unit in self.iter_units():
                for record_id in unit.iter_ids():
                    if record_id not in ids:
                        ids.append(record_id)
                        yield record_id

    def get(self, record_id: str) -> "Record":
        """
        Get record by ID.

        Args:
            record_id: record ID

        Returns:
            Record instance
        """

        return self._record_class(
            workspace=self.workspace,
            record_id=record_id,
            task=self.task,
            modality=self.modality,
        )

    # TODO: To test
    def logs(self) -> pd.DataFrame:
        """
        Returns:
            Logs history.
        """
        return pd.concat([rec.logs() for rec in self.all()])
