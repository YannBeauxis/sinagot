from sinagot.models import Subset


class BehaviorSubset(Subset):

    task = "HDC"

    def test(self):
        return "Test !!"
