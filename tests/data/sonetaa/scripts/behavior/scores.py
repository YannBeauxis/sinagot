# coding=utf-8

from sinagot import ScriptTemplate


class Script(ScriptTemplate):

    PATH_IN = ("HDC", "{id}", "Trial1_report.txt")
    PATH_OUT = ("PROCESSED", "{id}", "HDC", "behavior-scores.csv")

    def test_modif(self):
        return "test-before-modif"
