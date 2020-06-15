from sinagot.models import Record as RawRecord


class Record(RawRecord):

    task = "HDC"

    def test(self):
        return "Test record !!"
