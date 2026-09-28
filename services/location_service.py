import requests
from datetime import datetime


class LocationService:

    def __init__(self):

        self.last_location = None

        self.last_update = None

    def reverse_geocode(self, latitude, longitude):

        url = "https://nominatim.openstreetmap.org/reverse"

        params = {
            "lat": latitude,
            "lon": longitude,
            "format": "jsonv2",
            "zoom": 18,
            "addressdetails": 1
        }

        headers = {
            "User-Agent":
                "AI-Smart-EV-Charging-Project/1.0"
        }

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        address = data.get(
            "address",
            {}
        )

        locality = (
            address.get("suburb")
            or address.get("neighbourhood")
            or address.get("town")
            or address.get("village")
            or address.get("city")
            or "Unknown"
        )

        city = (
            address.get("city")
            or address.get("town")
            or address.get("municipality")
            or ""
        )

        district = (
            address.get("county")
            or ""
        )

        state = (
            address.get("state")
            or "Tamil Nadu"
        )

        country = (
            address.get("country")
            or "India"
        )

        postcode = (
            address.get("postcode")
            or ""
        )

        result = {

            "latitude": float(latitude),

            "longitude": float(longitude),

            "locality": locality,

            "city": city,

            "district": district,

            "state": state,

            "country": country,

            "postcode": postcode,

            "display_name":
                data.get(
                    "display_name",
                    locality
                ),

            "source":
                "OpenStreetMap Nominatim",

            "timestamp":
                datetime.now().strftime("%Y-%m-%d %I:%M:%S %p"),

            "is_live": True
        }

        self.last_location = result

        self.last_update = datetime.now()

        return result