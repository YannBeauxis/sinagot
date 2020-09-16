import re
import sinagot


def test_version_pattern():
    assert re.fullmatch(r"\d+\.\d+\.\d+", sinagot.__version__)
