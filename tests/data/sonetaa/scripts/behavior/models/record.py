from sinagot.models import Record as BaseRecord


class Record(BaseRecord):

    task = "HDC"

    def test(self):
        return "Test record !!"
