from pathlib import Path
from dask import visualize
from dask.delayed import Delayed
from dask.distributed import LocalCluster, Client, fire_and_forget
from sinagot.utils import get_module, get_script
from sinagot.run_manager import RunManager
from sinagot.config import ConfigurationError
from sinagot.run_manager import run_step_factory


class DaskRunManager(RunManager):
    """Manage multiple run in sequential or parallel mode"""

    def __init__(self, workspace):
        super().__init__(workspace)
        self.dask_config = workspace.config.get("dask", {})
        self.init_scheduler()

    def init_scheduler(self):
        scheduler_type = self.dask_config.get("scheduler", {}).get("type", "processes")
        if scheduler_type == "distributed":
            cluster_config = self.dask_config.get("cluster", {})
            self.scheduler = DaskDistributedScheduler(cluster_config)
        else:
            self.scheduler = DaskLocalScheduler(scheduler_type)

    def visualize(self, records, **kwargs):
        graph = DaskGraph(self.workspace)
        graph.build(records)
        return visualize(graph.dsk, **kwargs)

    def _run(self, records, run_opts):
        for record in records:
            graph = DaskGraph(self.workspace)
            graph.build(record, run_opts)
            dl = Delayed(("record", record.id), graph.dsk)
            self.scheduler.compute(dl)


class DaskLocalScheduler:
    def __init__(self, scheduler):
        self.scheduler = scheduler

    def compute(self, operation):
        return operation.compute(scheduler=self.scheduler)

    def close(self):
        pass


class DaskDistributedScheduler:

    _cluster = None
    _client = None

    def __init__(self, cluster_config):
        self.cluster_config = cluster_config

    def compute(self, operation):
        fire_and_forget(self.client.compute(operation))

    @property
    def client(self):
        if not self._client:
            self._init_client()
        return self._client

    def _init_client(self):
        self._client = Client(self.cluster)

    @property
    def cluster(self):
        if not self._cluster:
            self._init_cluster()
        return self._cluster

    def _init_cluster(self):
        cluster_config = self.cluster_config
        address = cluster_config.pop("address", None)
        if address:
            self._cluster = address
        else:
            self._cluster = LocalCluster(**cluster_config)

    def close(self):
        if self._client:
            self._client.close()
        if self._cluster:
            self._cluster.close()


class DaskGraph:
    def __init__(self, workspace):
        self.workspace = workspace
        self.dsk = {}

    @staticmethod
    def group(*args):
        pass

    def build(self, record, run_opts=None):
        # for record in records:
        task_outs = []
        if record.task:
            tasks = [record]
        else:
            tasks = record.iter_tasks()
        for task in tasks:
            mod_outs = []
            if task.modality:
                modalities = [task]
            else:
                modalities = task.iter_modalities()
            for modality in modalities:
                step = None
                prev_step = "raw"
                params = {
                    "record_id": modality.id,
                    "task": modality.task,
                    "modality": modality.modality,
                }
                for step in modality.steps.scripts_names():
                    target = self.add_step(prev_step, step, **params, run_opts=run_opts)
                    prev_step = step
                if step:
                    mod_outs.extend(target)
            task_outs.append(
                self.add_edge(
                    mod_outs,
                    self.group,
                    ("task", "{record_id}-{task}".format(**params)),
                )
            )
        self.add_edge(task_outs, self.group, ("record", "{record_id}".format(**params)))

    def add_edge(self, sources, func, target):
        graph = self.dsk
        graph.update({target: (func, *sources)})
        self.dsk = graph
        return target

    def add_step(self, source, target, record_id, task, modality, run_opts):

        step_params = {
            "workspace": self.workspace,
            "record_id": record_id,
            "task": task,
            "modality": modality,
        }

        func = run_step_factory(**step_params, step_label=target, run_opts=run_opts)

        script = get_script(**step_params, step_label=target)
        path_in = script.path.input
        if isinstance(path_in, dict):
            path_ins = path_in.values()
        else:
            path_ins = (path_in,)
        keys_in = tuple((source, self.format_path(p)) for p in path_ins)
        path_out = script.path.output
        if isinstance(path_out, dict):
            out_keys = [self.format_path(out_value) for out_value in path_out.values()]
            key_out = (target, *out_keys)
            res = []
            for out_value in out_keys:
                res_item = (target, out_value)
                self.add_edge(
                    ((target, *out_keys),), self.split_out, res_item,
                )
                res.append(res_item)

        else:
            key_out = (target, self.format_path(path_out))
            res = (key_out,)
        self.add_edge(keys_in, func, key_out)
        return res

    def format_path(self, path):
        try:
            path = path.relative_to(self.workspace.data_path)
        except ValueError:
            pass
        return str(path)
        # return path.relative_to(self.workspace.data_path)

    @staticmethod
    def split_out(*args):
        pass

    @staticmethod
    def get_path(script, direction):
        path = getattr(script.path, direction)
        if isinstance(path, Path):
            path = {"data": path}
        return path
