from sinagot import ScriptTemplate


class Script(ScriptTemplate):

    PATH_IN = {"first": ("raw", "{id}-first"), "second": ("raw", "{id}-second")}

    PATH_OUT = {
        "first": ("processed", "{id}-first"),
        "second": ("processed", "{id}-second"),
    }
