import re
import sinagot


def test_version_pattern():
    assert re.fullmatch(r"\d+\.\d+\.\d+", sinagot.__version__)


def test_default_workspace_version(workspace):
    assert workspace.version == "0.1.0"


def test_custom_workspace_version(custom_version_workspace):
    assert custom_version_workspace.version == "0.2.0"
