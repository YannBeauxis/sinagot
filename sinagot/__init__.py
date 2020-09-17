import pkg_resources
from sinagot.models import Workspace
from .script import ScriptTemplate


__all__ = ["Workspace", "ScriptTemplate"]

__version__ = pkg_resources.get_distribution("sinagot").version
