# coding=utf-8

from typing import Optional, Union
import pandas as pd
from sinagot.models import Model, Step, ScopedStep
from sinagot.utils import LOG_STEP_LABEL, LOG_STEP_STATUS
from sinagot.models.exceptions import NotFoundError, NotUnitError


class ModelWithStepCollection(Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.steps: StepCollection = self.set_step_collection()
        """Collection of steps."""

    def set_step_collection(self):
        if self.workspace.is_unit_mode:
            return StepCollectionUnit(self)
        return StepCollection(self)


class StepCollectionUnit(Model):
    """Manage the collection of all steps."""

    _MODEL_TYPE = "step_collection"
    _STEP_CLASS = Step
    task = None
    modality = None

    def __init__(self, model):
        """
        Params:
            model (instance): Parent model of the collection.
        """
        super().__init__(model.workspace)
        self.model = model

    def scripts_names(self):
        return self._scripts_config

    @property
    def _scripts_config(self):
        return self.workspace.config.get("steps", {}).get("scripts", [])

    def get(self, script_name: str) -> Step:
        """find a step by script name.

        Params:
            script_name: script label to find.

        Returns:
            `Step` instance.
        """
        return self._get(script_name)

    def _get(self, script_name):
        return self._STEP_CLASS(script=script_name, model=self.model)

    def first(self) -> Step:
        """Get the first step.

        Returns:
            `Step` instance.
        """
        return self._first()

    def _first(self):
        names = self.scripts_names()
        if not names:
            return None
        return self.get(names[0])

    def count(self) -> int:
        """

        Returns:
            number of steps.
        """
        return self._count()

    def _count(self):
        return len(self.scripts_names())

    def run(
        self,
        step_label: Optional[str] = None,
        force: Optional[bool] = False,
        ignore_missing: Optional[bool] = False,
        debug: Optional[bool] = False,
    ):
        """Run all steps of the scope.
        
        Args:
            step_label: if not `None`, run only for the step with this label.
            force: Force run and overwrites result file(s) if already exist(s).
            debug: If False, log scripts errors and not raise them.
        """

        workspace = self.workspace
        return workspace._run_manager.run(
            self.model,
            step_label=step_label,
            force=force,
            ignore_missing=ignore_missing,
            debug=debug,
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
                    self._record_status_unit(index, step)
                    for index, step in zip(range(self.count()), self._modality_all(),)
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
        for script_name in self.scripts_names():
            yield self.get(script_name)


class StepCollection(StepCollectionUnit):
    """Manage the collection of all steps of a scope."""

    _STEP_CLASS = ScopedStep

    def __init__(self, model):
        """
        Params:
            model (instance): Parent model of the collection.
        """
        super().__init__(model)
        self.task = self.model.task
        self.modality = self.model.modality

    def get(self, script_name: str) -> Union[Step, dict]:
        """find a step by script name.

        Params:
            script_name: script label to find.

        Returns:
            `Step` if model has modality, `dict` with `Step` or `None` as value for each modality either.
        """
        return self._modality_case_response("_get", script_name)

    def first(self) -> Union[Step, dict]:
        """Get the first step.

        Returns:
            `Step` if model has modality, `dict` with first step as value for each modality either.
        """
        return self._modality_case_response("_first")

    def count(self) -> Union[int, dict]:
        """Get the number of steps.

        Returns:
            `int` if model has modality, `dict` with step count as value for each modality either.
        """
        return self._modality_case_response("_count")

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

    def scripts_names(self):
        if self.modality:
            return self._modality_scripts_names()
        else:
            return {
                modality.modality: modality.steps._modality_scripts_names()
                for modality in self.model.iter_modalities()
            }

    def _modality_scripts_names(self):
        mod_config = self.workspace.config["modalities"].get(self.modality, {})
        shared_names = mod_config.get("scripts", [])
        task_scripts = mod_config.get("task_scripts", {})
        if self.task:
            task_names = task_scripts.get(self.task, [])
        else:
            task_names = [
                script for scripts in task_scripts.values() for script in scripts
            ]
        return shared_names + task_names
