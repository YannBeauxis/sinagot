import pandas as pd
from sinagot import ScriptTemplate


class Script(ScriptTemplate):

    PATH_IN = ("raw", "{id}-raw.csv")
    PATH_OUT = ("computed", "{id}-count.csv")

    def run(self):
        df = pd.read_csv(self.path.input)
        df = df.groupby("country").count()
        df.to_csv(self.path.output)
