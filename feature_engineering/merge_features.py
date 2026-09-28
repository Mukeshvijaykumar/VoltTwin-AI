from pathlib import Path
import pandas as pd

# -----------------------------
# Project Root
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------------
# Read Clean Data
# -----------------------------
weather = pd.read_csv(
    BASE_DIR / "datasets" / "final" / "weather_clean.csv"
)

grid = pd.read_csv(
    BASE_DIR / "datasets" / "final" / "grid_clean.csv"
)

print("\nWeather Dataset")
print(weather.head())

print("\nGrid Dataset")
print(grid.head())