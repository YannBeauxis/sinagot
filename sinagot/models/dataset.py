# coding=utf-8

import re
from pathlib import Path
from typing import Union, Optional
import toml
from sinagot.models import RecordCollection, Record, RunManager, Model
from sinagot.config import ConfigurationError
from sinagot.logger import logger_factory

try:
    from sinagot.plugins import DaskRunManager

    dask_enable = True
except ImportError:
    dask_enable = False


class Dataset(Model):
    """
    Dataset is the main class to handle data.
    It handle all configuration information and objects non specific to a particular data as the logger.
    It can also manage the [RecordCollection](record_collection.md) of all records with `.records` property.

    It required a configuration file in `.toml` format.

    Usage:

    ```python
    from sinagot import Dataset
    ds = Dataset(path/to/config.toml)
    ```
    """

    def __init__(
        self,
        config_path: Union[str, Path],
        data_path: Optional[Union[str, Path]] = None,
    ):
        """
        Arguments:
            config_path: path to the config file in toml.
            data_path: path to the folder of the dataset.
        """

        super().__init__(self)

        self._load_config(config_path)
        self._get_data_path(data_path)
        self._init_scripts_path()
        self._init_run_logger()
        self._init_run_manager()
        self._init_records()

    def _load_config(self, config_path):
        self._config_path = Path(config_path)
        if self._config_path.is_dir():
            self._config_path = self._config_path / "dataset.toml"
        self.config = toml.load(self._config_path)
        """Config dictionnary from config file."""

    @property
    def scripts_path(self) -> Path:
        """Path of all the scripts folder"""
        return self._scripts_path

    def _init_scripts_path(self):
        try:
            self._scripts_path = self._resolve_path(self.config["path"]["scripts"])
        except KeyError:
            self._scripts_path = self._config_path.parent

    def _init_run_logger(self):
        self.logger = logger_factory(self.config)
        """Logger of the dataset"""

    def _init_run_manager(self):
        try:
            run_mode = self.config["run"]["mode"]
        except KeyError:
            run_mode = "main_process"
        if run_mode == "dask":
            if not dask_enable:
                raise ConfigurationError("Dask is not enable in this environment")
            run_manager = DaskRunManager
        else:
            run_manager = RunManager

        self._run_manager = run_manager(self)

    @property
    def data_path(self) -> Path:
        """Path of data folder"""
        return self._data_path

    def _get_data_path(self, data_path):
        if data_path is None:
            data_path = self.config["path"].get("data", self._config_path)
        self._data_path = self._resolve_path(data_path)

    def _resolve_path(self, raw_path):
        """Resolve path from config from raw_path and self.config_path if raw path
        is relative to current dir i.e. begin with './' or '...'

        Args:
            raw_path (str or pathlib.Path): path from config to resolve

        Returns:
            pathlib.Path: absolute path
        """

        path = Path(raw_path)
        if re.match(r"(?:\.{1,2}\/.*|\.$)", str(raw_path)):
            path = Path(self._config_path.parent, raw_path).resolve()
        return path

    @property
    def records(self) -> RecordCollection:
        """RecordCollection of all records of the dataset"""
        return self._records

    @property
    def steps(self) -> "StepCollection":
        """StepCollecion for all steps of the dataset"""
        return self._records.steps

    def _init_records(self):

        RecordCollection._set_subscopes(self)
        Record._set_subscopes(self)

        self._records = RecordCollection(self)
        self._DEPRECATED_alias_records()
        self._alias_subscopes()

    def _alias_subscopes(self):
        ALIASES = self.records._tasks + self.records._modalities
        for alias in ALIASES:
            setattr(self, alias, getattr(self.records, alias))

    def _DEPRECATED_alias_records(self):
        ALIASES = [
            "dataset",
            "ids",
            "get",
            "first",
            "all",
            "count",
            "has",
            "count_detail",
            "iter_tasks",
            "tasks",
            "task",
            "iter_modalities",
            "modality",
            "modalities",
            "run",
            "_MODEL_TYPE",
            "_subscope_class",
        ]
        for alias in ALIASES:
            setattr(self, alias, getattr(self.records, alias))
