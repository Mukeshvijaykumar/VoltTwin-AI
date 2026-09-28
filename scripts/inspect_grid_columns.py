import pandas as pd

file = "datasets/raw/grid/dgr2-2026-07-23.xls"

df = pd.read_excel(file, header=None)

print("=" * 80)
print("Shape")
print(df.shape)

print("=" * 80)
print("First 25 Rows")

print(df.head(25))

print("=" * 80)

print("Column Count :", len(df.columns))

print(df.columns.tolist())