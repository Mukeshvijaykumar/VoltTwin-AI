import os
import requests


api_key = os.getenv("ELECTRICITY_MAPS_API_KEY")

url = "https://api.electricitymaps.com/v4/zones"

headers = {
    "auth-token": api_key
}

response = requests.get(
    url,
    headers=headers,
    timeout=10
)

print("Status:", response.status_code)

data = response.json()

print("\nINDIA / TAMIL NADU RELATED ZONES")
print("=" * 60)

for key, zone in data.items():

    country = zone.get("countryName", "")
    display = zone.get("displayName", "")
    zone_key = zone.get("zoneKey", "")

    if (
        "India" in country
        or "Tamil" in display
        or "IN" in zone_key
    ):

        print("\nZone Key:", zone_key)
        print("Name:", display)
        print("Country:", country)
        print("Access:", zone.get("access"))