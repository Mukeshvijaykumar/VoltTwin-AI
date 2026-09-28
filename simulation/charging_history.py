import pandas as pd
from pathlib import Path


class ChargingHistory:

    def __init__(self):

        self.file = (
            Path(__file__).resolve().parent.parent
            / "datasets"
            / "processed"
            / "charging_history.csv"
        )

    def save(self, record):

        df = pd.DataFrame([record])

        if self.file.exists():

            old = pd.read_csv(self.file)

            df = pd.concat(
                [old, df],
                ignore_index=True
            )

        df.to_csv(
            self.file,
            index=False
        )

        print("Charging history updated.")