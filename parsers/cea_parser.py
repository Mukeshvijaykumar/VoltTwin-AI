from pathlib import Path
import pandas as pd

from parsers.hierarchy import Hierarchy
from parsers.cleaner import normalize

from config.india_states import INDIAN_STATES
from config.india_regions import REGIONS


class CEAParser:

    def __init__(self):

        self.base = Path(__file__).resolve().parent.parent

        self.file = (
            self.base
            / "datasets"
            / "raw"
            / "grid"
            / "dgr2-2026-07-23.xls"
        )

        self.hierarchy = Hierarchy()
        self.records = []
    def read(self):
        return pd.read_excel(
            self.file,
            header=None,
            skiprows=5
        )

    def detect(self):

        df = self.read()

        for _, row in df.iterrows():

            

            text = normalize(row[0])

            if text in ["", "nan", "NaN", "NaT"]:

                continue

            # ----------------------------
            # Ignore unwanted rows
            # ----------------------------
            if text in ["STATE TOTAL", "REGION TOTAL", "Unit"]:
                continue

            if text in REGIONS:

                self.hierarchy.set_region(text)

                print(f"\nREGION : {text}")

                continue

            if text in INDIAN_STATES:

                self.hierarchy.set_state(text)

                print(f"STATE : {text}")

                continue

            if text.startswith("SECTOR"):

                print("SECTOR FOUND")

                continue
            

            # ----------------------------
            # Detect Type
            # ----------------------------
            if text.startswith("TYPE"):

                print("TYPE FOUND :", text)

                continue

            # ----------------------------
            # Otherwise -> Power Station
            # ----------------------------
            record = {

    "Region": self.hierarchy.region,

    "State": self.hierarchy.state,

    "Power_Station": text,

    "Installed_Capacity_MW": row[7],

    "Metric_1": row[8],

    "Metric_2": row[9],

    "Today_Program": row[10],

    "Today_Actual": row[11]

                    }

            

            self.records.append(record)

            print(record)

        df = pd.DataFrame(self.records)

        output = (
    self.base
    / "datasets"
    / "processed"
    / "grid_final.csv"
        )

        df.to_csv(output, index=False)

        print("\nSaved Successfully")
        print(output)

        print("\nFirst Five Rows")
        print(df.head())

        print("\nTotal Power Stations :", len(df))
        
if __name__ == "__main__":

    parser = CEAParser()

    parser.detect()