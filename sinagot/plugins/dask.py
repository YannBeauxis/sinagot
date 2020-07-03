import json
import asyncio
import dask
from dask.distributed import LocalCluster, Client, Future
from sinagot.models import Record, RunManager
from sinagot.config import ConfigurationError


class DaskRunManager(RunManager):
    """Manage multiple run in sequential or parallel mode"""

    cluster = None
    _client = None

    def __init__(self, dataset):
        super().__init__(dataset)
        self.dask_config = dataset.config.get("dask", {})
        self.scheduler_config = self.dask_config.get("scheduler", {})
        # self.init_scheduler()

    def init_scheduler(self):
        mode = self.scheduler_config.pop("mode", "local")
        scheduler_config = self.scheduler_config
        for key, default_value in (
            ("dashboard_address", None),
            ("scheduler_port", 8786),
        ):
            scheduler_config[key] = scheduler_config.get(key, default_value)
        if mode == "local":
            try:
                self.cluster = LocalCluster(**self.scheduler_config)
                self.scheduler_address = self.cluster.scheduler_address
            except OSError:
                self.scheduler_address = "127.0.0.1: " + str(
                    scheduler_config["scheduler_port"]
                )
        elif mode == "distributed":
            self.scheduler_address = scheduler_config["scheduler_address"]
        else:
            raise ConfigurationError("{} model is not enable for dask".format(mode))

    def _init_client(self):
        self._client = Client(self.scheduler_address)

    @property
    def client(self):
        if not self._client:
            self._init_client()
        return self._client

    def close(self):
        if self.client:
            self.client.close()
        if self.cluster:
            self.cluster.close()

    def _run(self, records):
        # futures = {
        #     ("tasks", record.id): self.dask_futures(self.record_structure(record))
        #     for record in records
        # }

        # from pprint import pprint

        # pprint(self.record_structure(list(records)[0]))

        records = list(records)

        def run_tasks(*args):
            pass

        def run_modalities(*args):
            pass

        def run_step(*args):
            print(("run_step", *args))
            return ("run_step", *args)

        graph = dict()

        for record in records:
            tasks = self.record_structure(record)
            record_tasks = []
            for task_name, modalities in tasks.items():
                task_modalities = []
                task_key = record.id + "-" + task_name
                record_tasks.append(("run_modalities", task_key))
                for modality, steps in modalities.items():
                    steps.reverse()
                    prev_step = steps.pop(0)
                    last_step_label = prev_step["step_label"]
                    modality_key = task_key + "-" + modality
                    task_modalities.append((last_step_label, modality_key))
                    prev_step_key = modality_key  # + "--" + last_step_label
                    graph[(last_step_label, prev_step_key)] = (
                        run_step,
                        ("run_modalities", "step_input"),
                    )
                    for step in steps:
                        step_key = modality_key + "--" + step["step_label"]
                        graph[(prev_step["step_label"], prev_step_key)] = (
                            run_step,
                            (step["step_label"], step_key),
                        )
                        prev_step_key = step_key
                        prev_step = step
                    graph[(prev_step["step_label"], prev_step_key)] = (
                        run_step,
                        ("raw_data", step_key),
                    )
                graph[("run_modalities", task_key)] = (
                    run_modalities,
                    *task_modalities,
                )
            graph[("run_tasks", record.id)] = (
                run_tasks,
                *record_tasks,
            )

        return graph

        # all_runs = dask.delayed(futures)
        # # all_runs.compute()
        # return all_runs

    def dask_futures(self, target, label=None):
        if isinstance(target, dict):
            return self.dask_parallel_futures(target, label=label)
        else:
            return self.dask_steps_future(target)

    def dask_parallel_futures(self, collection, label=None):
        def func(*args):
            return args

        return {
            "RS": [("func", "some"), ("func", "some_chose")],
            "MMN": [("func", "other"),],
        }

        # if label:
        #     func.__name__ = label
        #     if label == "tasks":
        #         label = "modalities"
        # return dask.delayed(func)(
        #     self.dask_futures(item, label=label) for item in collection.values()
        # )

    def dask_steps_future(self, collection):

        delayed = None
        for item in collection:
            delayed = dask.delayed(self.run_step_factory(item))(delayed)
        return delayed

    ########################

    def _run_(self, records):

        futures = [
            self.dask_futures(self.record_structure(record)) for record in records
        ]

        asynchronous = self.dask_config.get("asynchronous", False)
        return self.client.gather(futures, asynchronous=asynchronous)

    def dask_parallel_futures_(self, collection):
        def func(*args):
            return args

        return self.client.map(
            func, [self.dask_futures(item) for item in collection.values()]
        )

    def dask_steps_future_(self, collection):

        future = None

        for item in collection:
            func = self.run_step_factory(item)
            future = self.client.submit(func, future)

        return future
