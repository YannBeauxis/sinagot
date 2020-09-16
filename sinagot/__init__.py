from pathlib import Path
import toml
from sinagot.models import Workspace
from .script import ScriptTemplate


__all__ = ["Workspace", "ScriptTemplate"]

conf_path = Path(__file__).parents[1] / "pyproject.toml"
conf = toml.loads(conf_path.read_text())
__version__ = conf["tool"]["poetry"]["version"]
