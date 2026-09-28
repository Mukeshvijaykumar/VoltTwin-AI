"""
=========================================================
weather_downloader.py

Purpose:
    Download live weather data from Open-Meteo API
    Validate the received data
    Save historical weather records to CSV

Author : Mukesh
Project:
Multi-Agent AI-Based Smart Slab and Thermal-Aware EV Charging
=========================================================
"""

import requests
import pandas as pd
import os
from datetime import datetime


class WeatherDownloader:

    def __init__(self):

        # Chennai Coordinates
        self.latitude = 13.0827
        self.longitude = 80.2707

        # Folder
        self.folder = "datasets/weather"

        # CSV File
        self.file = os.path.join(
            self.folder,
            "weather.csv"
        )

    # ---------------------------------------------
    # Download Weather
    # ---------------------------------------------
    def get_weather(self):

        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={self.latitude}"
            f"&longitude={self.longitude}"
            f"&current="
            f"temperature_2m,"
            f"relative_humidity_2m,"
            f"cloud_cover,"
            f"wind_speed_10m"
        )

        try:

            response = requests.get(
                url,
                timeout=10
            )

            response.raise_for_status()

            data = response.json()

            current = data["current"]

            weather = {

                "timestamp": datetime.now(),

                "temperature":
                current["temperature_2m"],

                "humidity":
                current["relative_humidity_2m"],

                "cloud_cover":
                current["cloud_cover"],

                "wind_speed":
                current["wind_speed_10m"]

            }

            return weather

        except Exception as e:

            print("\nError Downloading Weather")

            print(e)

            return None

    # ---------------------------------------------
    # Validate Weather
    # ---------------------------------------------
    def validate_weather(
            self,
            weather
    ):

        if weather is None:
            return False

        if not (-20 <= weather["temperature"] <= 60):
            return False

        if not (0 <= weather["humidity"] <= 100):
            return False

        if not (0 <= weather["cloud_cover"] <= 100):
            return False

        if weather["wind_speed"] < 0:
            return False

        return True

    # ---------------------------------------------
    # Save Weather
    # ---------------------------------------------
    def save_weather(
            self,
            weather
    ):

        os.makedirs(
            self.folder,
            exist_ok=True
        )

        df = pd.DataFrame([weather])

        if os.path.exists(self.file):

            old_df = pd.read_csv(self.file)

            df = pd.concat(
                [old_df, df],
                ignore_index=True
            )

        df.to_csv(
            self.file,
            index=False
        )

        print("\nWeather Saved")

        print(self.file)

    # ---------------------------------------------
    # Run
    # ---------------------------------------------
    def run(self):

        print("=" * 40)

        print("Weather Downloader")

        print("=" * 40)

        weather = self.get_weather()

        if self.validate_weather(weather):

            print("\nWeather Data")

            print(weather)

            self.save_weather(weather)

        else:

            print("\nInvalid Weather")


if __name__ == "__main__":

    downloader = WeatherDownloader()

    downloader.run()