from pathlib import Path
import pandas as pd


class Extract:

    def __init__(self):

        self.base = Path(__file__).resolve().parent.parent

    def read_weather(self):

        file = self.base / "datasets" / "raw" / "weather" / "weather.csv"

        return pd.read_csv(file)

    def read_grid(self):

        file = self.base / "datasets" / "processed" / "grid.csv"

        return pd.read_csv(file)