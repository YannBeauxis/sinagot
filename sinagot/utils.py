import re
from importlib import import_module, util as importutil
from pathlib import Path
from functools import wraps

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


def handle_dict(func):
    """Decorator to apply method to all values of dict if first arg is dict"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        args = list(args)
        arg = args.pop(0)
        if isinstance(arg, dict):
            return {key: func(value, *args, **kwargs) for key, value in arg.items()}
        else:
            return func(arg, *args, **kwargs)

    return wrapper


def handle_dict_bool(func):
    """
    Decorator to apply method that returns a boolean to all values of dict
    and check if all results are True
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        result = handle_dict(func)(*args, **kwargs)
        if isinstance(result, dict):
            return all(result.values())
        else:
            return result

    return wrapper


class PathManager:
    def __init__(self, scope, path_tuple):
        self.scope = scope
        self.workspace = scope.workspace
        self.root_path = self.workspace.data_path
        self.path_tuple = path_tuple

    def exists(self):
        path = self.root_path / self.format_pattern()
        print(path)
        return path.exists()

    def format_pattern(self, *args, **kwargs):
        return self.raw_pattern.format(
            id="{}".format(self.id_pattern(*args, **kwargs)),
            task="{}".format(self.task_pattern(*args, **kwargs)),
        )

    @property
    def raw_pattern(self):
        return str(Path(*self.path_tuple))

    def id_pattern(self, *args, **kwargs):
        return getattr(self.scope, "id", None)

    def task_pattern(self, *args, **kwargs):
        return self.scope.task


class PathCollection:

    _PATH_MANGER_CLASS = PathManager

    def __init__(self, scope, path):
        self.scope = scope
        if isinstance(path, dict):
            self.path_tuples = path.values()
        else:
            self.path_tuples = (path,)

    @property
    def path_managers(self):
        return (self._PATH_MANGER_CLASS(self.scope, path) for path in self.path_tuples)


class PathChecker(PathCollection):
    def exists(self):
        return all(pm.exists() for pm in self.path_managers)


class PathManagerGlob(PathManager):
    def iter_ids(self):
        for path in self.root_path.glob(self.glob_pattern):
            match = self.re_pattern.match(str(path))
            if match:
                yield match.group(1)

    @property
    def glob_pattern(self):
        return self.format_pattern("glob")

    @property
    def re_pattern(self):
        path = str(self.root_path / self.format_pattern("re"))
        return re.compile(path)

    def id_pattern(self, pattern_type):
        record_id = getattr(self.scope, "id", None)
        if record_id:
            return record_id
        elif pattern_type == "re":
            return "({})".format(self.workspace.config["records"]["id_pattern"])
        elif pattern_type == "glob":
            return "*"

    def task_pattern(self, pattern_type):
        task = self.scope.task
        if task:
            return task
        elif pattern_type == "re":
            return "(?:.*)"
        elif pattern_type == "glob":
            return "*"


class PathExplorer(PathCollection):

    _PATH_MANGER_CLASS = PathManagerGlob

    def iter_ids(self):
        ids = []
        for path_manager in self.path_managers:
            for record_id in path_manager.iter_ids():
                if record_id not in ids:
                    ids.append(record_id)
                    yield record_id

