from pathlib import Path
import pytest
from sinagot.utils import handle_dict, handle_dict_bool, PathChecker, PathExplorer


def test_handle_dict():
    SINGLE_ARG = 2
    DICT_ARG = {"A": 1, "B": 2}

    @handle_dict
    def multiply(arg, factor=2):
        return arg * factor

    assert multiply(SINGLE_ARG) == SINGLE_ARG * 2
    dict_result = {key: value * 2 for key, value in DICT_ARG.items()}
    assert multiply(DICT_ARG) == dict_result

    factor = 3
    assert multiply(SINGLE_ARG, factor=factor) == SINGLE_ARG * factor
    dict_result = {key: value * factor for key, value in DICT_ARG.items()}
    assert multiply(DICT_ARG, factor=factor) == dict_result

    @handle_dict_bool
    def is_superior(arg, value=0):
        return arg > value

    assert is_superior(SINGLE_ARG)
    assert is_superior(DICT_ARG)
    assert not is_superior(DICT_ARG, value=1)


PATH_MFF = ("MFF", "{id}-{task}.mff")
PATH_HDC = ("PROCESSED", "{id}", "HDC", "behavior-scores.csv")
PATH_DICT = {"MFF": PATH_MFF, "HDC": PATH_HDC}


def test_path_checker(workspace, record):

    path_check = PathChecker(record.RS, PATH_MFF)
    assert path_check.exists()
    path_check = PathChecker(workspace.RS.get("REC-012345-A"), PATH_MFF)
    assert not path_check.exists()
    path_dict = {
        "score": PATH_HDC,
        "score_norm": ("PROCESSED", "{id}", "HDC", "norm-scores.csv"),
    }
    path_check = PathChecker(workspace.records.get("REC-200320-A"), path_dict)
    assert path_check.exists()
    path_check = PathChecker(record.RS, PATH_DICT)
    assert path_check.exists()
    path_check = PathChecker(record.RS, path_dict)
    assert not path_check.exists()


@pytest.mark.parametrize(
    "path", (PATH_MFF, PATH_HDC, {"MFF": PATH_MFF, "HDC": PATH_HDC})
)
def test_path_explorer(workspace, IDS, path):

    path_expl = PathExplorer(workspace.RS, path)
    assert set(IDS) == set(path_expl.iter_ids())

