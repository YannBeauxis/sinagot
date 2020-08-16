# coding=utf-8

from sinagot import ScriptTemplate


class Script(ScriptTemplate):

    PATH_IN = ("PROCESSED", "{id}", "HDC", "behavior-scores.csv")
    PATH_OUT = ("PROCESSED", "{id}", "HDC", "norm-scores.csv")

    def run(self):
        try:
            text = self.path.input.read_text()
        except:
            text = "no input"
        self.path.output.write_text(text)
