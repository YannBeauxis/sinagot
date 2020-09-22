from sinagot.models import Model


def test_repr(workspace):
    class TestModel(Model):
        pass

    test = TestModel(workspace)
    assert str(test) == "<TestModel instance>"
