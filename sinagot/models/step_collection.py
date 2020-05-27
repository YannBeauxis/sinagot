# coding=utf-8

from typing import Optional, Union
import pandas as pd
from sinagot.models import Model, Step
from sinagot.utils import LOG_STEP_LABEL, LOG_STEP_STATUS
from sinagot.models.exceptions import NoModalityError, NotFoundError, NotUnitError


class StepCollection(Model):
    """Manage the collection of all steps of a scope."""

    _MODEL_TYPE = "step_collection"

    def __init__(self, model):
        """
        Params:
            model (instance): Parent model of the collection.
        """
        super().__init__(model.dataset)
        self.model = model
        self.task = self.model.task
        self.modality = self.model.modality

    def get(self, script_name: str) -> Union[Step, dict]:
        """find a step by script name.

        Params:
            script_name: script label to find.

        Returns:
            `Step` if model has modality, `dict` with `Step` or `None` as value for each modality either.
        """
        return self._modality_case_response("_modality_get", script_name)

    def _modality_get(self, script_name):
        if not self.model.modality:
            raise NoModalityError
        return Step(script=script_name, model=self.model)

    def first(self) -> Union[Step, dict]:
        """Get the first step.

        Returns:
            `Step` if model has modality, `dict` with first step as value for each modality either.
        """
        return self._modality_case_response("_modality_first")

    def _modality_first(self):
        if not self.model.modality:
            raise NoModalityError
        names = self._modality_scripts_names()
        if not names:
            return None
        return self.get(names[0])

    def count(self) -> int:
        """Get the number of steps.

        Returns:
            `int` if model has modality, `dict` with step count as value for each modality either.
        """
        return self._modality_case_response("_modality_count")

    def _modality_count(self):
        if not self.model.modality:
            raise NoModalityError
        return len(self._scripts_names())

    def _modality_case_response(self, method, *args):
        if self.model.modality:
            return getattr(self, method)(*args)
        else:
            return {
                modality.modality: modality.steps._modality_case_default(method, *args)
                for modality in self.model.iter_modalities()
            }

    def _modality_case_default(self, method, *args):
        try:
            return getattr(self, method)(*args)
        except NotFoundError:
            return None

    def run(
        self,
        step_label: Optional[str] = None,
        force: Optional[bool] = False,
        debug: Optional[bool] = False,
    ):
        """Run all steps of the scope.
        
        Args:
            step_label: if not `None`, run only for the step with this label.
            force: Force run and overwrites result file(s) if already exist(s).
            debug: If False, log scripts errors and not raise them.
        """

        dataset = self.dataset
        return dataset._run_manager.run(
            self.model, step_label=step_label, force=force, debug=debug
        )

    def status(self) -> pd.DataFrame:
        """Get status of all steps

        Returns:
            A pandas DataFrame with a row for each step.
        """
        if self.model._MODEL_TYPE == "record":
            return self._record_status()
        elif self.model.count() == 0:
            return pd.DataFrame([])
        else:
            return pd.concat([rec.steps.status() for rec in self.model.all()])

    def _record_status(self):
        if self.count():
            return pd.DataFrame(
                [
                    unit.steps._record_status_unit(index, step)
                    for unit in self.model.iter_units()
                    for index, step in zip(
                        range(unit.steps.count()), unit.steps._modality_all()
                    )
                ]
            )
        else:
            return None

    def _record_status_unit(self, index, step):
        model = self.model
        if not model.is_unit:
            raise NotUnitError
        return {
            "record_id": self.model.id,
            "task": self.task,
            "modality": self.modality,
            "step_index": index + 1,
            LOG_STEP_LABEL: step.label,
            LOG_STEP_STATUS: step.status(),
        }

    def _modality_all(self):
        for script_name in self._scripts_names():
            yield self.get(script_name)

    def _scripts_names(self):
        if self.modality:
            return self._modality_scripts_names()
        else:
            return {
                modality.modality: modality.steps._modality_scripts_names()
                for modality in self.model.iter_modalities()
            }

    def _modality_scripts_names(self):
        mod_config = self.dataset.config["modalities"].get(self.modality, {})
        shared_names = mod_config.get("scripts", [])
        task_scripts = mod_config.get("tasks_scripts", {})
        if self.task:
            task_names = task_scripts.get(self.task, [])
        else:
            task_names = [
                script for scripts in task_scripts.values() for script in scripts
            ]
        return shared_names + task_names
