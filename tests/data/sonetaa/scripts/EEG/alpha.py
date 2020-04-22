from sinagot import ScriptTemplate


class Script(ScriptTemplate):

    PATH_IN = ("PREPROCESSED", "{id}-{task}-epo.fif.gz")
    PATH_OUT = ("PROCESSED", "{id}", "alpha")
