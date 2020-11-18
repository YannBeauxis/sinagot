from sinagot.utils import handle_dict, handle_dict_bool


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


# def test_path_explorer():
