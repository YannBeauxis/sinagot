from pathlib import Path
from dask import visualize
from dask.delayed import Delayed
from dask.distributed import LocalCluster, Client, fire_and_forget
from sinagot.models import Model, Record, RunManager
from sinagot.config import ConfigurationError


class DaskRunManager(RunManager):
    """Manage multiple run in sequential or parallel mode"""

    _cluster = None
    _client = None

    def __init__(self, dataset):
        super().__init__(dataset)
        self.dask_config = dataset.config.get("dask", {})
        self.scheduler_config = self.dask_config.get("scheduler", {})
        # self.init_scheduler()

    def _init_cluster(self):
        print("_init_cluster")
        scheduler_config = self.scheduler_config
        mode = scheduler_config.pop("mode", "local")

        # for key, default_value in (
        #     ("dashboard_address", None),
        #     ("scheduler_port", 8786),
        # ):
        #     scheduler_config[key] = scheduler_config.get(key, default_value)
        if mode == "local":
            print("mode == local")
            # try:
            self._cluster = LocalCluster(**self.scheduler_config)
        #         self.scheduler_address = self.cluster.scheduler_address
        #     except OSError:
        #         self.scheduler_address = "127.0.0.1: " + str(
        #             scheduler_config["scheduler_port"]
        #         )
        # elif mode == "distributed":
        # self.scheduler_address = scheduler_config["scheduler_address"]
        # else:
        #     raise ConfigurationError("{} model is not enable for dask".format(mode))

    def _init_client(self):
        # self._client = Client(self.scheduler_address)
        self._client = Client(self.cluster)

    @property
    def cluster(self):
        if not self._cluster:
            self._init_cluster()

    @property
    def client(self):
        if not self._client:
            self._init_client()
        return self._client

    def close(self):
        if self._client:
            self._client.close()
        if self._cluster:
            self._cluster.close()

    def visualize(self, records, **kwargs):
        graph = DaskGraph(self.dataset)
        graph.build(records)
        return visualize(graph.dsk, **kwargs)

    def _run(self, records):
        records = list(records)
        for record in records:
            graph = DaskGraph(self.dataset)
            graph.build(record)
            visualize(graph.dsk, filename=r"{}.svg".format(record.id))
            # print(graph.dsk)
            dl = Delayed(("record", record.id), graph.dsk)
            fire_and_forget(self.client.compute(dl))



class DaskGraph(Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dsk = {}

    @staticmethod
    def group(*args):
        pass

    def build(self, record):
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
                    target = self.add_step(prev_step, step, **params)
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
        self.add_edge(
            task_outs, self.group, ("record", "{record_id}".format(**params))
        )

    def add_edge(self, sources, func, target):
        graph = self.dsk
        graph.update({target: (func, *sources)})
        self.dsk = graph
        return target

    def add_step(self, source, target, **kwargs):

        script = self.get_script(**kwargs, step_label=target)
        func = self.run_step_factory(**kwargs, step_label=target)

        path_in = script.path.input
        if isinstance(path_in, dict):
            path_ins = path_in.values()
        else:
            path_ins = (path_in,)
        keys_in = tuple((source, self.format_path(p)) for p in path_ins)
        path_out = script.path.output
        if isinstance(path_out, dict):
            out_keys =  [self.format_path(out_value) for out_value in path_out.values()]
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
        return str(path.relative_to(self.dataset.data_path))

    @staticmethod
    def split_out(*args):
        pass

    @staticmethod
    def get_path(script, direction):
        path = getattr(script.path, direction)
        if isinstance(path, Path):
            path = {"data": path}
        return path

    def run_step_factory(self, record_id, task, modality, step_label):
        script_class = self._get_module("Script", modality, step_label)
        script = script_class(
            data_path=self.dataset.data_path,
            id_=record_id,
            task=task,
            logger_namespace=self.logger.name,
        )

        def func(*args, **kwargs):
            # to_run = kwargs.get("step_label") == step_label
            to_run = True
            if to_run:
                script._run()
                # script._run(**kwargs)
                # return arg

        func.__name__ = step_label
        return func

    def get_script(self, record_id, task, modality, step_label):
        script_class = self._get_module("Script", modality, step_label)
        return script_class(
            data_path=self.dataset.data_path,
            id_=record_id,
            task=task,
            logger_namespace=self.logger.name,
        )
