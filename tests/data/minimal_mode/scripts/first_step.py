from sinagot import ScriptTemplate


class Script(ScriptTemplate):

    PATH_IN = ("RAW", "{id}.txt")
    PATH_OUT = ("PROCESSED", "{id}.csv")
