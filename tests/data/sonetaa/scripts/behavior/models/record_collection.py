from sinagot.models import RecordCollection as RawRecordCollection


class RecordCollection(RawRecordCollection):

    task = "HDC"

    def test(self):
        return "Test !!"
