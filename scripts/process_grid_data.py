from pathlib import Path
import pandas as pd

# ----------------------------
# Project Paths
# ----------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

GRID_FILE = BASE_DIR / "datasets" / "raw" / "grid" / "dgr2-2026-07-23.xls"

OUTPUT_FOLDER = BASE_DIR / "datasets" / "processed"

OUTPUT_FOLDER.mkdir(exist_ok=True)

OUTPUT_FILE = OUTPUT_FOLDER / "grid.csv"

# ----------------------------
# Read Government Report
# ----------------------------

df = pd.read_excel(
    GRID_FILE,
    header=None,
    skiprows=5
)

records = []

current_region = ""
current_state = ""

for _, row in df.iterrows():

    name = str(row[0]).strip()

    if name == "nan":
        continue

    # ----------------------------
    # Region
    # ----------------------------

    if name.isupper() and "TOTAL" not in name and len(name) > 3:

        if name not in ["STATE TOTAL", "REGION TOTAL"]:

            current_region = name

        continue

    # ----------------------------
    # State
    # ----------------------------

    if name == "STATE TOTAL":
        continue

    # Skip unwanted rows

    if "SECTOR" in name:
        continue

    if "TYPE" in name:
        continue

    if name == "Unit":
        continue

    if "TOTAL" in name:
        continue

    # ----------------------------
    # Power Station
    # ----------------------------

    capacity = row[7]

    today_program = row[8]

    today_actual = row[9]

    records.append({

        "Region": current_region,

        "Power_Station": name,

        "Capacity_MW": capacity,

        "Today's_Program": today_program,

        "Today's_Actual": today_actual

    })

# ----------------------------
# Save
# ----------------------------

clean_df = pd.DataFrame(records)

clean_df.to_csv(
    OUTPUT_FILE,
    index=False
)

print(clean_df.head())

print()

print("Total Stations :", len(clean_df))

print("Saved to")

print(OUTPUT_FILE)