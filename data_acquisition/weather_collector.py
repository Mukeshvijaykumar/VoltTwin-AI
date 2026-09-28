import requests
import pandas as pd
from pathlib import Path
from datetime import datetime

# -----------------------------
# Project Root
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------------
# Save Folder
# -----------------------------
SAVE_FOLDER = BASE_DIR / "datasets" / "raw" / "weather"
SAVE_FOLDER.mkdir(parents=True, exist_ok=True)

SAVE_FILE = SAVE_FOLDER / "weather.csv"

# -----------------------------
# Tamil Nadu Cities
# -----------------------------
cities = {
    "Chennai": (13.0827, 80.2707),
    "Coimbatore": (11.0168, 76.9558),
    "Madurai": (9.9252, 78.1198),
    "Salem": (11.6643, 78.1460),
    "Tiruchirappalli": (10.7905, 78.7047)
}

weather_records = []

# -----------------------------
# Download Weather
# -----------------------------
for city, (lat, lon) in cities.items():

    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}"
        f"&longitude={lon}"
        f"&current="
        f"temperature_2m,"
        f"relative_humidity_2m,"
        f"cloud_cover,"
        f"wind_speed_10m"
    )

    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to fetch data for {city}")
        continue

    data = response.json()

    current = data["current"]

    weather_records.append({
        "timestamp": datetime.now(),
        "city": city,
        "temperature": current["temperature_2m"],
        "humidity": current["relative_humidity_2m"],
        "cloud_cover": current["cloud_cover"],
        "wind_speed": current["wind_speed_10m"]
    })

# -----------------------------
# Create DataFrame
# -----------------------------
df = pd.DataFrame(weather_records)

print(df)

# -----------------------------
# Save CSV
# -----------------------------
df.to_csv(SAVE_FILE, index=False)

print("\nSaved Successfully")
print("Location :", SAVE_FILE)