from pathlib import Path
import pandas as pd
import numpy as np

BASE = Path(__file__).resolve().parent.parent

# Read master dataset
df = pd.read_csv(
    BASE / "datasets" / "processed" / "master_dataset.csv"
)

# Make results reproducible

df["Installed_Capacity_MW"] = df["Installed_Capacity_MW"].fillna(0)

df["Today_Actual"] = df["Today_Actual"].fillna(0)

df["Today_Program"] = df["Today_Program"].fillna(0)
# -----------------------------
# Create synthetic EV demand
# -----------------------------
np.random.seed(42)
df["ev_demand"] = (
    0.40 * df["Today_Actual"]
    + 0.15 * df["Installed_Capacity_MW"]
    + np.random.normal(0, 50, len(df))
)

# Ensure demand is not negative
df["ev_demand"] = df["ev_demand"].clip(lower=0)
df = df.dropna()
# Save
output = (
    BASE / "datasets" / "processed" / "training_dataset.csv"
)

df.to_csv(output, index=False)

print("Training Dataset Created Successfully")
print(output)
print()
print(df.head())