from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parent.parent

# -----------------------------
# Read datasets
# -----------------------------

weather = pd.read_csv(
    BASE / "datasets" / "processed" / "weather_clean.csv"
)

grid = pd.read_csv(
    BASE / "datasets" / "processed" / "grid_final.csv"
)

print("Weather Shape :", weather.shape)
print("Grid Shape    :", grid.shape)

# -----------------------------
# Use the latest weather record
# -----------------------------

latest_weather = weather.iloc[-1]

# -----------------------------
# Copy weather to every station
# -----------------------------

grid["temperature"] = latest_weather["temperature"]

grid["humidity"] = latest_weather["humidity"]

grid["wind_speed"] = latest_weather["wind_speed"]

grid["cloud_cover"] = latest_weather["cloud_cover"]

# -----------------------------
# Save
# -----------------------------

output = (
    BASE
    / "datasets"
    / "processed"
    / "master_dataset.csv"
)

grid.to_csv(output, index=False)

print("\nMaster Dataset Created Successfully")

print(output)

print()

print(grid.head())

print()

print("Total Records :", len(grid))