from sinagot import ScriptTemplate


class Script(ScriptTemplate):

    PATH_IN = ("MFF", "{id}-{task}.mff")
    PATH_OUT = ("PREPROCESSED", "{id}-{task}-epo.fif.gz")

    def run(self):
        self.path.output.write_text("done")
