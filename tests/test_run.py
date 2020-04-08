import toml
import time
from sinagot import Dataset
from sinagot.utils import StepStatus
from sinagot.plugins import DaskRunManager


def test_main_process(dataset):
    dataset.run()


def test_dask(shared_datadir):

    # Change config to activate dask
    config_path = shared_datadir / "sonetaa" / "dataset.toml"
    config = toml.load(config_path)
    config["run"]["mode"] = "dask"
    config_path.write_text(toml.dumps(config))

    ds = Dataset(shared_datadir / "sonetaa")
    assert isinstance(ds._run_manager, DaskRunManager)
    rec = ds.get("REC-200320-A").HDC.EEG
    step = rec.steps.get("preprocess")
    assert step.status() == StepStatus.PROCESSING
    # TODO: Handle asyncio
    rec.run()
    assert step.status() == StepStatus.DONE
