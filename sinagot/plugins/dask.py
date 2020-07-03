import json
import asyncio
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
        self.init_scheduler()

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
