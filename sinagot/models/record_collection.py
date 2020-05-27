# coding=utf-8

import os
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

    def ids(self) -> Generator[str, None, None]:
        """Generator all record ids within the record_collection.
        
        Returns:
            Record ID.
        """
        # TODO: use dataset cache for ids
        if self.is_unit:
            for record_id in self._ids_unit():
                yield record_id
        else:
            units = self.iter_units()
            ids = []
            for unit in units:
                for record_id in unit.ids():
                    if not record_id in ids:
                        ids.append(record_id)
                        yield record_id

    def _ids_unit(self):
        """Return the list of all records ids i.e. subfolder names"""
        ids = []
        config = self.config
        try:
            file_match = config["modalities"][self.modality]["file_match"]
        except KeyError:
            file_match = config["records"]["file_match"]

        first_script = self.steps.first()

        if first_script:
            path_in = first_script.script.PATH_IN
            if isinstance(path_in, dict):
                path_in = path_in.values()
            else:
                path_in = [path_in]
            for p_in in path_in:
                pattern = os.path.join(*p_in)
                path_ = p_in
                if not file_match[0]:
                    path_ = path_[:-1]
                pattern = os.path.join(*path_)
                pattern = pattern.format(
                    id="({})".format(config["records"]["id_pattern"]),
                    task="(?:{})".format(self.task),
                )
                root_path = os.path.join(self.dataset.data_path, p_in[0])
                for root, dirs, files in os.walk(root_path):
                    if file_match[1]:
                        # Search ID wihtin files
                        item_set = files
                    else:
                        # Search ID wihtin dirs
                        item_set = dirs
                    for item in item_set:
                        path = os.path.join(root, item)
                        m = re.search(pattern, path)
                        if m and (len(m.groups()) > 0):
                            record_id = m.group(1)
                            if record_id not in ids:
                                ids.append(record_id)
                                yield record_id

    def all(self) -> Generator["Record", None, None]:
        """Generate all records instances of the record_collection.
        
        Returns:
            sinagot.models.Record: Record instance
        """

        for record_id in self.ids():
            yield self.get(record_id)

    def first(self) -> "Record":
        """
        Get the first record found.
        
        Returns:
            Record instance
        """

        for record_id in self.ids():
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

        for id_ in self.ids():
            if id_ == record_id:
                return True
        return False

    def count(self) -> int:
        """
        Count all records.

        Returns:
            Number of records.
        """

        return sum(1 for rec in self.ids())

    # TODO: To test
    def count_detail(self, *args, **kwargs) -> pd.DataFrame:
        """
        Returns:
            Number of records present in each tasks and modalities.

        Note:
            Refer to [`Record.count_detail()`](record.md#sinagot.models.record.Record.count_detail) 
            for more information
        """

        count = None

        self.logger.debug("Begin count_detail")
        for rec in self.all():
            self.logger.debug("Begin count_detail for record {}".format(rec.id))
            try:
                count_ = rec.count_detail(*args, **kwargs)
                if count is None:
                    count = count_
                    columns = count.columns
                else:
                    count = count.append(count_)
                    if "count_x" in count.columns:
                        count = count.eval("count = count_x + count_y").reindex(
                            columns, axis=1
                        )
            except:
                self.logger.warning(
                    "Error in count_detail for record {}".format(rec.id)
                )

        return count.groupby(list(columns[:-1])).sum().reset_index()

    # TODO: To test
    def logs(self) -> pd.DataFrame:
        """
        Returns:
            Logs history.
        """
        return pd.concat([rec.logs() for rec in self.all()])
