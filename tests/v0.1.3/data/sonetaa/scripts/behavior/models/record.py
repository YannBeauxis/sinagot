from sinagot.models import Record


class BehaviorRecord(Record):

    task = "HDC"

    def test(self):
        return "Test record !!"
