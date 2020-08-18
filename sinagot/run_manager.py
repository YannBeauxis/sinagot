from sinagot.utils import get_script


class RunManager:
    """Manage multiple run in sequential or parallel mode"""

    def __init__(self, workspace):
        self.workspace = workspace

    def run(self, model, **run_opts):

        if model._MODEL_TYPE == "record":
            records = [model]
        else:
            records = model.all()

        return self._run(records, run_opts)

    @staticmethod
    def record_structure(record):
        return record._structure_status(("record_id", "task", "modality", "step_label"))

    def _run(self, records, run_opts):

        for record in records:
            shape = self.record_structure(record)
            for task in shape.values():
                for modality in task.values():
                    for step in modality:
                        step_kw = {
                            key: step[key]
                            for key in ("record_id", "task", "modality", "step_label")
                        }
                        run_step_factory(self.workspace, **step_kw, run_opts=run_opts)()

    def close(self):
        pass


def run_step_factory(workspace, record_id, task, modality, step_label, run_opts):
    script = get_script(
        workspace=workspace,
        record_id=record_id,
        task=task,
        modality=modality,
        step_label=step_label,
    )

    run_opts_ = run_opts.copy()
    step_label_filter = run_opts_.pop("step_label", None)
    to_run = step_label_filter in [step_label, None]

    def func(*args):
        if to_run:
            script._run(**run_opts_)

    func.__name__ = step_label
    return func
