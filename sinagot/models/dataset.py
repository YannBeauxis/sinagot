# coding=utf-8

import re
from pathlib import Path
from typing import Union, Optional
import toml
import pandas as pd
from sinagot.models import Subset, Record, RunManager
from sinagot.config import ConfigurationError
from sinagot.logger import logger_factory

try:
    from sinagot.plugins import DaskRunManager

    dask_enable = True
except ImportError:
    dask_enable = False


class Dataset(Subset):
    """
    Dataset is the main class to handle data.
    It handle all configuration information and objects non specific to a particular data as the logger.
    It's also a [Subset](subset.md) instance used to manipulate a collection off all the records.

    It required a configuration file in toml format.

    Usage:

    ```python
    from sinagot import Dataset
    ds = Dataset(path/to/config.toml)
    ```
    """

    _subscope_class = Subset

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

        # Load config
        self._config_path = Path(config_path)
        if self._config_path.is_dir():
            self._config_path = self._config_path / "dataset.toml"
        self.config = toml.load(self._config_path)
        """Config dictionnary from config file."""

        # Get data_path
        if data_path is None:
            data_path = self.config["path"].get("data", self._config_path)
        self._data_path = self._resolve_path(data_path)

        # Get _scripts_path from config
        try:
            self._scripts_path = self._resolve_path(self.config["path"]["scripts"])
        except KeyError:
            self._scripts_path = self._config_path.parent

        # Init logger
        self.logger = logger_factory(self.config)
        """Logger of the dataset"""

        # Init Run management
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

        #  Init from subset
        super().__init__(self)

        # Set subscope from config to Subset and Record class
        Subset._set_subscopes(self)
        Record._set_subscopes(self)

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
