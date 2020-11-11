from importlib import import_module, util as importutil
from pathlib import Path

LOG_ORIGIN = "log_from"
LOG_STEP_LABEL = "step_label"
LOG_RECORD_ID = "record_id"
LOG_STEP_STATUS = "step_status"
LOG_VERSION = "workspace_version"


class StepStatus:

    INIT = 0
    DATA_READY = 10
    PROCESSING = 20
    DONE = 30
    ERROR = 40
    DATA_NOT_AVAILABLE = 41


def record_log_file_path(data_path, rec_id):
    return data_path / "LOG" / "{}.log".format(rec_id)


def get_module(workspace, class_name, *args):
    """Import a module from scripts folder"""

    path = Path(workspace._scripts_path, *args)
    spec = importutil.spec_from_file_location(
        ".".join(args[-3:]), path.with_suffix(".py")
    )
    module = importutil.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, class_name)


def get_plugin_modules(plugin_model):

    plugin = import_module("sinagot.plugins.models." + plugin_model)
    return getattr(plugin, "MODELS")


def get_script(workspace, record_id, task, modality, step_label):
    if modality:
        script_class = get_module(workspace, "Script", modality, step_label)
    else:
        script_class = get_module(workspace, "Script", step_label)
    return script_class(
        data_path=workspace.data_path,
        record_id=record_id,
        task=task,
        logger_namespace=workspace.logger.name,
        workspace_version=workspace.version,
    )
