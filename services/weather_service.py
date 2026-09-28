import requests
from datetime import datetime


class WeatherService:

    def __init__(self):

        self.timezone = "Asia/Kolkata"

        self.last_weather = None

        self.last_fetch = None

    def get_weather(
        self,
        latitude,
        longitude,
        location_name="Current Location"
    ):

        url = (
            "https://api.open-meteo.com/v1/forecast"
        )

        params = {

            "latitude": latitude,

            "longitude": longitude,

            "current": (
                "temperature_2m,"
                "relative_humidity_2m,"
                "apparent_temperature,"
                "precipitation,"
                "rain,"
                "cloud_cover,"
                "wind_speed_10m,"
                "wind_direction_10m"
            ),

            "timezone":
                self.timezone
        }

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        current = data["current"]

        weather = {

            "temperature":
                current["temperature_2m"],

            "apparent_temperature":
                current["apparent_temperature"],

            "humidity":
                current["relative_humidity_2m"],

            "precipitation":
                current["precipitation"],

            "rain":
                current["rain"],

            "cloud_cover":
                current["cloud_cover"],

            "wind_speed":
                current["wind_speed_10m"],

            "wind_direction":
                current["wind_direction_10m"],

            "timestamp":
                current["time"],

            "latitude":
                latitude,

            "longitude":
                longitude,

            "location":
                location_name,

            "source":
                "Open-Meteo",

            "is_live":
                True
        }

        self.last_weather = weather

        self.last_fetch = datetime.now()

        return weather