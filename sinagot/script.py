# coding=utf-8
"""Common functions used for script"""

import logging
from pathlib import Path
from typing import Optional
from collections import namedtuple
from json_log_formatter import JSONFormatter
from concurrent_log_handler import ConcurrentRotatingFileHandler
from sinagot.utils import (
    record_log_file_path,
    LOG_ORIGIN,
    LOG_STEP_LABEL,
    LOG_RECORD_ID,
    LOG_STEP_STATUS,
    LOG_VERSION,
    StepStatus,
)


class ScriptTemplate:
    """
    Template class for scripts. You must override `PATH_IN`, `PATH_OUT` and `run()` to use it.

    Usage:
        From harbor example :

            import pandas as pd
            from sinagot import ScriptTemplate

            class Script(ScriptTemplate):

                PATH_IN = ("raw", "{id}-raw.csv")
                PATH_OUT = ("computed", "{id}-count.csv")

                def run(self):
                    df = pd.read_csv(self.path.input)
                    df = df.groupby("country").count()
                    df.to_csv(self.path.output)
    """

    _PATH_LABELS = ["input", "output"]
    PATH_IN = ("FOLDER_IN", "{id}-{task}.in")
    """tuple or dict of tuples to specify input path pattern"""
    PATH_OUT = ("FOLDER_OUT", "{id}-{task}.out")
    PATH_CONTROL = ("FOLDER_CONTROL", "{id}-{task}.control")
    """tuple or dict of tuples to specify output path pattern"""

    debug = False
    _logger_file_handler = None
    _logger = None
    logger = None
    modality = None
    """The modality label"""

    def __init__(
        self,
        data_path: str,
        record_id: str,
        task: Optional[str] = None,
        opts={},
        logger_namespace: Optional[str] = None,
        workspace_version=None,
    ):

        self.status = StepStatus.INIT
        """
        Status of the script during its run. Valuse are defined in sinagot.utils.StepStatus class"""
        self._workspace_version = workspace_version
        self.data_path = data_path
        """The path to dataset"""
        self.id = record_id
        """The record ID"""
        self.task = task
        """The modality label"""
        module_split = self.__class__.__module__.split(".")
        if len(module_split) > 1:
            self.modality = module_split[-2]
        self.label = module_split[-1]
        "The step label"
        self.opts = opts
        "Optional dict"
        self._logger_namespace = logger_namespace

        self._set_path()

    def _init_logger(self, debug=False):
        file_handler_path = record_log_file_path(self.data_path, self.id)
        file_handler = ConcurrentRotatingFileHandler(
            file_handler_path, "a", 512 * 1024, 5
        )
        file_formatter = JSONFormatter()
        file_handler.setFormatter(file_formatter)
        file_handler.addFilter(self._log_filter_factory())
        self._logger_file_handler = file_handler
        logger_ = logging.getLogger(self._logger_namespace)
        if debug:
            log_level = logging.DEBUG
        else:
            log_level = logging.INFO
        logger_.setLevel(log_level)
        self._logger = logger_
        logger = logging.LoggerAdapter(logger_, self._log_extra(StepStatus.PROCESSING))
        self.logger = logger

    def _log_filter_factory(self):
        record_id = self.id

        def record_filter(record):
            return record.__dict__[LOG_RECORD_ID] == record_id

        return record_filter

    def _log_extra(self, status):
        return {
            LOG_ORIGIN: "script",
            LOG_VERSION: self._workspace_version,
            LOG_RECORD_ID: self.id,
            "scope": "record",
            "task": self.task,
            "modality": self.modality,
            LOG_STEP_LABEL: self.label,
            LOG_STEP_STATUS: status,
        }

    def _set_path(self):

        ScriptPath = namedtuple("IOPath", self._PATH_LABELS + ["control"])
        self.path = ScriptPath(
            input=self._get_path(self.PATH_IN),
            output=self._get_path(self.PATH_OUT),
            control=self._get_path(self.PATH_CONTROL),
        )

    def _get_path(self, raw_path):

        if isinstance(raw_path, tuple):
            return Path(self.data_path, *self._str_path(raw_path))
        if isinstance(raw_path, dict):
            return {
                label: Path(self.data_path, *self._str_path(rp))
                for label, rp in raw_path.items()
            }

    def _str_path(self, raw_path_unit: tuple):
        return (
            rp.format(id=self.id, task=self.task, **self.opts) for rp in raw_path_unit
        )

    def _run(
        self, force: bool = False, ignore_missing: bool = False, debug: bool = False
    ):
        """Required run function. Called by step model :code:`run()` method."""
        self.debug = debug
        self._init_logger(debug)
        self._logger.addHandler(self._logger_file_handler)
        self._log_status("Init run", StepStatus.INIT, debug=True)
        if not all(self.data_exist.input.values()) and not ignore_missing:
            missing = [
                str(key) for key, exist in self.data_exist.input.items() if not exist
            ]
            self._log_status(
                "Input data %s not available", StepStatus.DATA_NOT_AVAILABLE, missing,
            )
        elif not self._has_to_run(force):
            self._log_status("Run already processed", StepStatus.DONE, debug=True)
        else:
            self.status = StepStatus.PROCESSING
            self._log_status("Processing run", StepStatus.PROCESSING)
            try:
                self._mkdir_output()
                self.run()
                self._log_status("Run finished", StepStatus.DONE)
            except Exception as ex:
                if debug:
                    raise ex
                self._log_status(ex, StepStatus.ERROR)

        self._logger.removeHandler(self._logger_file_handler)

        return True

    def _log_status(
        self, message, status, args=[], debug=False,
    ):
        if debug:
            self._logger.debug(message, *args, extra=self._log_extra(status))
        else:
            self._logger.info(message, *args, extra=self._log_extra(status))

    def run(self):
        """Main method called during step run."""
        self.logger.info("Running ...")

    @property
    def data_exist(self):
        """Get named tuple of boolean to check if input and output data exist."""
        DataStatus = namedtuple("IOPath", self._PATH_LABELS)
        return DataStatus(*(self._path_exist(target) for target in self._PATH_LABELS))

    def _path_exist(self, target):
        return {path: path.exists() for path in self._iter_paths(target)}

    def _mkdir_output(self):
        for path in self._iter_paths("output"):
            if not path.parent.exists():
                # exist_ok=True to avoid race condition
                path.parent.mkdir(parents=True, exist_ok=True)

    def _iter_paths(self, target):
        if target not in ("input", "output"):
            raise AttributeError("target not in ('input', 'output')")
        paths = getattr(self.path, target)
        if isinstance(paths, Path):
            return (paths,)
        return paths.values()

    def _has_to_run(self, force):
        if force:
            return True
        for path in self._iter_paths("output"):
            if not path.exists():
                return True
        return False
