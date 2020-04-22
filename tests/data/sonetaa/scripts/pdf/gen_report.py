# coding=utf-8

from sinagot import ScriptTemplate


class Script(ScriptTemplate):

    PATH_IN = ("PROCESSED", "{id}")
    PATH_OUT = ("PROCESSED", "{id}", "report.pdf")
