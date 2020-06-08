import json
import asyncio
from dask.distributed import LocalCluster, Client, Future
from sinagot.models import Record, RunManager
from sinagot.config import ConfigurationError


class DaskRunManager(RunManager):
    """Manage multiple run in sequential or parallel mode"""

    cluster = None
    client = None

    def __init__(self, dataset):
        super().__init__(dataset)
        self.dask_config = dataset.config.get("dask", {})
        self.scheduler_config = self.dask_config.get("scheduler", {})
        self.init_client()

    def init_client(self):
        mode = self.scheduler_config.pop("mode", "local")
        if mode == "local":
            cluster = LocalCluster(**self.scheduler_config)
            self.dataset.scheduler_address = cluster.scheduler_address
            self.cluster = cluster
        elif mode == "distributed":
            self.dataset.scheduler_address = self.scheduler_config["scheduler_address"]
        else:
            raise ConfigurationError("{} model is not enable for dask".format(mode))
        self.client = Client(cluster.scheduler_address)

    def _run(self, records):

        futures = [
            self.dask_futures(self.record_structure(record)) for record in records
        ]

        asynchronous = self.dask_config.get("asynchronous", False)
        return self.client.gather(futures, asynchronous=asynchronous)

    def close(self):
        if self.client:
            self.client.close()
        if self.cluster:
            self.cluster.close()

    def dask_futures(self, target):
        if isinstance(target, dict):
            return self.dask_parallel_futures(target)
        else:
            return self.dask_steps_future(target)

    def dask_parallel_futures(self, collection):
        def func(*args):
            return args

        return self.client.map(
            func, [self.dask_futures(item) for item in collection.values()]
        )

    def dask_steps_future(self, collection):

        future = None

        for item in collection:
            func = self.run_step_factory(item)
            future = self.client.submit(func, future)

        return future
