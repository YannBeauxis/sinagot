from sinagot import ScriptTemplate


class Script(ScriptTemplate):

    PATH_IN = ("PROCESSED", "{id}.csv")
    PATH_OUT = ("PROCESSED", "{id}.txt")
