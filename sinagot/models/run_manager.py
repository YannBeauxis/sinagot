from sinagot.models import Model, Step, Record


class RunManager(Model):
    """Manage multiple run in sequential or parallel mode"""

    kwargs = {}

    def run(self, model, **kwargs):

        self.kwargs = kwargs

        if model._MODEL_TYPE == "record":
            records = [model]
        else:
            records = model.all()

        return self._run(records)

    @staticmethod
    def record_structure(record):
        return record._structure_status(("record_id", "task", "modality", "step_label"))

    def _run(self, records):

        for record in records:
            shape = self.record_structure(record)
            for task in shape.values():
                for modality in task.values():
                    for step in modality:
                        self.run_step_factory(step)(None)

    def run_step_factory(self, step):
        id_ = step["record_id"]
        task = step["task"]
        modality = step["modality"]
        step_label = step["step_label"]
        script_class = self._get_module("Script", modality, step_label)
        script = script_class(
            data_path=self.dataset.data_path,
            id_=id_,
            task=task,
            logger_namespace=self.logger.name,
        )

        force = self.kwargs.get("force", False)
        debug = self.kwargs.get("debug", False)
        to_run = (self.kwargs.get("step_label") or step_label) == step_label

        def func(arg):
            if to_run:
                script._run(force=force, debug=debug)
                return arg

        return func

    def close(self):
        pass
