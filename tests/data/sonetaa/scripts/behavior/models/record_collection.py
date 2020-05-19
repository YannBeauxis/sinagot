from sinagot.models import RecordCollection


class BehaviorRecordCollection(RecordCollection):

    task = "HDC"

    def test(self):
        return "Test !!"
