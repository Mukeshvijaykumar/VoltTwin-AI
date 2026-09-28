import pandas as pd

file = "datasets/raw/grid/dgr2-2026-07-23.xls"

df = pd.read_excel(file, header=None)

# Find the first occurrence of PANIPAT TPS
for index, row in df.iterrows():

    if str(row[0]).strip() == "PANIPAT TPS":

        print("=" * 80)
        print("Row Number :", index)
        print("=" * 80)

        for i, value in enumerate(row):

            print(f"Column {i:2d} : {value}")

        break