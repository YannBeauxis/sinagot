# coding=utf-8
"""Common functions used for script"""

import logging
from pathlib import Path
from collections import namedtuple
from json_log_formatter import JSONFormatter
from sinagot.utils import (
    record_log_file_path,
    LOG_ORIGIN,
    LOG_STEP_LABEL,
    LOG_RECORD_ID,
    LOG_STEP_STATUS,
    StepStatus,
)


class ScriptTemplate:
    """
        Template class for scripts

        Args:
            data_path (str): Folder path of data corresponding
                to :code:`data_path` attribute of dataset or record models.
            id_ (str): Id of the record or task to run the script.
            task (str): Taks label
    """

    _PATH_LABELS = ["input", "output"]
    PATH_IN = ("FOLDER_IN", "{id}-{task}.in")
    PATH_OUT = ("FOLDER_OUT", "{id}-{task}.out")

    _logger_file_handler = None
    _logger = None
    logger = None
    modality = None

    def __init__(self, data_path, id_, task, opts={}, logger_namespace=None):

        self.status = StepStatus.INIT
        self.data_path = data_path
        self.id = id_
        self.task = task
        module_split = self.__class__.__module__.split(".")
        if len(module_split) > 1:
            self.modality = module_split[-2]
        self.label = module_split[-1]

        self.opts = opts

        self._logger_namespace = logger_namespace

        self._set_path()

    def _init_logger(self):
        file_handler_path = record_log_file_path(self.data_path, self.id)
        file_handler = logging.FileHandler(file_handler_path)
        file_formatter = JSONFormatter()
        file_handler.setFormatter(file_formatter)
        self._logger_file_handler = file_handler
        logger_ = logging.getLogger(self._logger_namespace)
        logger_.setLevel(logging.INFO)
        self._logger = logger_
        logger = logging.LoggerAdapter(logger_, self._log_extra(StepStatus.PROCESSING))
        self.logger = logger

    def _log_extra(self, status):
        return {
            LOG_ORIGIN: "script",
            LOG_RECORD_ID: self.id,
            "scope": "record",
            "task": self.task,
            "modality": self.modality,
            LOG_STEP_LABEL: self.label,
            LOG_STEP_STATUS: status,
        }

    def _set_path(self):

        ScriptPath = namedtuple("IOPath", self._PATH_LABELS)
        self.path = ScriptPath(
            input=self._get_path(self.PATH_IN), output=self._get_path(self.PATH_OUT),
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

    def _run(self, force: bool = False, debug: bool = False):
        """Required run function. Called by step model :code:`run()` method."""

        self._init_logger()
        self._logger.addHandler(self._logger_file_handler)
        self._log_status("Init run", StepStatus.INIT)
        if not all(self.data_exist.input.values()):
            missing = [key for key, value in self.data_exist.input.items()]
            self._log_status(
                "Input data  %s not available", StepStatus.DATA_NOT_AVIABLE, missing
            )
        elif not self._has_to_run(force):
            self._log_status("Run already processed", StepStatus.DONE)
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

    def _log_status(self, message, status, *args):
        self._logger.info(message, *args, extra=self._log_extra(status))

    def run(self):
        self.logger.info("Running ...")

    @property
    def data_exist(self):
        DataStatus = namedtuple("IOPath", self._PATH_LABELS)
        return DataStatus(*(self._path_exist(target) for target in self._PATH_LABELS))

    def _path_exist(self, target):
        # for path in self._iter_paths(target):
        #     if not path.exists():
        #         return False
        # return True
        return {path: path.exists() for path in self._iter_paths(target)}

    def _mkdir_output(self):
        for path in self._iter_paths("output"):
            if not path.parent.exists():
                path.parent.mkdir(parents=True)

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
            if (not path.exists()) or path.read_text() == "":
                return True
        return False
