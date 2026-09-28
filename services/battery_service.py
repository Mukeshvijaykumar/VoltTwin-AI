import random
from datetime import datetime


class BatteryService:

    def __init__(self):

        self.soc = 42.0
        self.temperature = 37.0
        self.health = 96.0
        self.current = 0.0

    def get_battery_status(self):

        return {
            "soc": round(self.soc, 2),
            "temperature": round(self.temperature, 2),
            "health": round(self.health, 2),
            "current": round(self.current, 2),
            "timestamp": datetime.now().isoformat(),
            "source": "BMS Telemetry Simulator",
            "is_live": True
        }

    def simulate_charging(self, current):

        self.current = current

        if current > 0:

            self.soc += 0.8

            temperature_rise = current * 0.02

            self.temperature += temperature_rise

        else:

            self.temperature -= 0.1

        self.temperature = max(
            20,
            min(60, self.temperature)
        )

        self.soc = min(
            100,
            self.soc
        )

        return self.get_battery_status()