# coding=utf-8

import inspect
from typing import Optional
from pathlib import Path
import pandas as pd
from sinagot.models import Model
from sinagot.utils import StepStatus, LOG_STEP_LABEL, LOG_STEP_STATUS
from sinagot.models.exceptions import NotFoundError, NoModalityError


class Step(Model):

    _REPR_ATTRIBUTES = ["scope", "task", "modality", "label"]
    _MODEL_TYPE = "step"
    label = None
    id = None

    def __init__(self, script, model):

        if not model.modality:
            raise NoModalityError
        self.model = model
        self.task = model.task
        self.modality = model.modality
        super().__init__(model.dataset)

        if inspect.isclass(script):
            script_class = script
            self.label = script.__class__.__name__
        elif isinstance(script, str):
            try:
                script_class = self._get_module("Script", self.modality, script)
            except FileNotFoundError as ex:
                raise NotFoundError from ex
            self.label = script
        else:
            raise AttributeError("Type {} is not valid for script".format(type(script)))

        if model._MODEL_TYPE == "record":
            self.id = model.id

        self.script_class = script_class
        self.script = script_class(
            data_path=self.dataset.data_path,
            id_=self.id,
            task=self.task,
            logger_namespace=self.logger.name,
        )

    def status(self) -> int:
        """Get status code.

        Returns:
            sinagot.utils.StepStatus value
        """
        if self._script_path_exists("output"):
            return StepStatus.DONE
        try:
            logs = self.logs()
            status = logs[logs[LOG_STEP_STATUS].notna()].iloc[0][LOG_STEP_STATUS]
        except:
            status = None
        if status in [StepStatus.PROCESSING, StepStatus.ERROR]:
            return status
        if self._script_path_exists("input"):
            return StepStatus.DATA_READY
        else:
            return StepStatus.INIT

    def _script_path_exists(self, position: str) -> bool:
        path = getattr(self.script.path, position)
        if isinstance(path, Path):
            return path.exists()
        if isinstance(path, dict):
            return all([p.exists() for p in path.values()])

    def run(self, force: Optional[bool] = False):
        """
        Run the step script.
        
        Args:
            force: Force run and overwrites result file(s) if already exist(s).
        """
        self.model.run(step_label=self.label, force=force)

    def logs(self) -> pd.DataFrame:
        """
        Returns:
            Logs history.
        """
        try:
            return self.model.logs().query(
                "{} == '{}'".format(LOG_STEP_LABEL, self.label)
            )
        except:
            return pd.DataFrame()
