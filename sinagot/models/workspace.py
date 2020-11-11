# coding=utf-8

import re
from pathlib import Path
from typing import Union, Optional
import toml
from sinagot.models import (
    RecordCollection,
    RecordCollectionUnit,
    Record,
    RecordUnit,
    Model,
)
from sinagot.config import ConfigurationError
from sinagot.logger import logger_factory
from sinagot.run_manager import RunManager

try:
    from sinagot.plugins.dask import DaskRunManager

    dask_enable = True
except ImportError:
    dask_enable = False


class Workspace(Model):
    """
    Workspace is the main class to handle dataset and scripts. It required a configuration file in `.toml` format.
    
    You can access to the [RecordCollection](record_collection.md) of the dataset with `.records` property.
    
    You can access to the [StepCollection](step_collection.md) of the scripts with `.steps` property.

    Usage:
        Create an instance :
        
            from sinagot import Workspace
            ws = Workspace(path/to/config.toml)
    """

    _record_unit_class = RecordUnit
    _record_class = Record
    _record_collection_unit_class = RecordCollectionUnit
    _record_collection_class = RecordCollection

    DEFAULT_VERSION = "0.1.0"
    DEFAULT_CONFIG = {
        "path": {"dataset": "./dataset", "scripts": "./scripts"},
        "run": {"mode": "main_process"},
    }

    def __init__(
        self,
        config_path: Union[str, Path],
        data_path: Optional[Union[str, Path]] = None,
        scripts_path: Optional[Union[str, Path]] = None,
    ):
        """
        Arguments:
            config_path: path to the config file in toml.
            data_path: path to the folder of the workspace.
        """

        super().__init__(self)

        self._load_config(config_path)
        self._set_data_path(data_path)
        self._set_scripts_path(scripts_path)
        self._init_run_logger()
        self._init_run_manager()
        self._init_records()

    @property
    def version(self):
        return self.DEFAULT_VERSION

    def _load_config(self, config_path):
        self._config_path = Path(config_path)
        if self._config_path.is_dir():
            self._config_path = self._config_path / "workspace.toml"
        config = toml.load(self._config_path)
        for section, values in self.DEFAULT_CONFIG.items():
            if section not in config:
                config[section] = values
        self.config = config
        """Config dictionnary from config file."""
        self.is_unit_mode = not any(
            scope in self.config for scope in ("tasks", "modalities")
        )

    def _set_data_path(self, data_path):
        if data_path is None:
            data_path = self.config["path"].get("dataset", self._config_path)
        self._data_path = self._resolve_path(data_path)

    @property
    def data_path(self) -> Path:
        """Path of data folder"""
        return self._data_path

    def _set_scripts_path(self, scripts_path):
        scripts_path = scripts_path or self.config.get("path", {}).get("scripts")
        if scripts_path:
            self._scripts_path = self._resolve_path(scripts_path)
        else:
            self._scripts_path = self._config_path.parent

    @property
    def scripts_path(self) -> Path:
        """Path of all the scripts folder"""
        return self._scripts_path

    def _init_run_logger(self):
        self.logger = logger_factory(self.config, self.is_unit_mode)
        """Logger of the workspace"""
        log_path = self.data_path / "LOG"
        if not log_path.exists():
            log_path.mkdir()

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
        """RecordCollection of all records of the workspace"""
        return self._records

    @property
    def steps(self) -> "StepCollection":
        """StepCollecion for all steps of the workspace"""
        return self._records.steps

    def _init_records(self):

        if self.is_unit_mode:
            self._record_collection_unit_class.__name__ = "RecordCollection"
            self._record_unit_class.__name__ = "Record"
            self._records = self._record_collection_unit_class(self)
        else:
            self._records = self._record_collection_class(self)
            self._record_collection_class._set_subscopes(self)
            self._record_class._set_subscopes(self)
            self._alias_subscopes()

    def _alias_subscopes(self):
        ALIASES = self.records._tasks + self.records._modalities
        for alias in ALIASES:
            setattr(self, alias, getattr(self.records, alias))

    def close(self):
        self._run_manager.close()
