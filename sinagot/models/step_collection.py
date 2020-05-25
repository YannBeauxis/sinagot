# coding=utf-8

from typing import Optional
import pandas as pd
from sinagot.models import Model, Step
from sinagot.utils import LOG_STEP_LABEL, LOG_STEP_STATUS


class StepCollection(Model):
    """Manage all steps of a category.

    Args:
        model (instance): Parent model of the collection.

    Attributes:
        model (instance): Parent model of the collection.

    """

    _MODEL_TYPE = "step_collection"

    def __init__(self, model):

        super().__init__(model.dataset)
        self.model = model
        self.task = self.model.task
        self.modality = self.model.modality

    @property
    def _scripts_names(self):
        try:
            sn = self.dataset.config["modalities"][self.modality]["scripts"]
        except KeyError:
            return []
        try:
            return (
                sn
                + self.dataset.config["modalities"][self.modality]["tasks_scripts"][
                    self.task
                ]
            )
        except KeyError:
            return sn

    def get_script(self, script_name):
        return self._get_module("Script", self.modality, script_name)

    def get(self, script):
        return Step(script=script, model=self.model)

    def all(self):
        for script_name in self._scripts_names:
            yield self.get(script_name)

    def find(self, pattern):

        for script_name in self._scripts_names:
            if pattern in script_name:
                yield self.get(script_name)

    def first(self):
        """Get the first step.

        Returns:
            instance: Step instance
        """

        return self.get(self._scripts_names[0])

    def count(self):
        return len(self._scripts_names)

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
            dataset, step_label=step_label, force=force, debug=debug
        )

    def status(self):
        if self.model._MODEL_TYPE == "record":
            if self.count() > 0:
                return pd.DataFrame(
                    [
                        {
                            "record_id": self.model.id,
                            "task": self.task,
                            "modality": self.modality,
                            "step_index": index,
                            LOG_STEP_LABEL: step.label,
                            LOG_STEP_STATUS: step.status(),
                        }
                        for index, step in zip(range(1, self.count() + 1), self.all())
                    ]
                )
            else:
                return None
        elif self.model.count() == 0:
            return None
        else:
            return pd.concat(
                [rec.status() for rec in self.model.all() if rec.status() is not None]
            )
