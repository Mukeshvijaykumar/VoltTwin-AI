from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")


class ChargingScheduler:

    def __init__(
        self,
        battery_capacity_kwh=40.0,
        charger_power_kw=7.36
    ):
        self.battery_capacity_kwh = float(
            battery_capacity_kwh
        )

        self.charger_power_kw = float(
            charger_power_kw
        )

    def normalize_time(self, value):

        if value is None:
            return datetime.now(IST)

        if value.tzinfo is None:
            return value.replace(tzinfo=IST)

        return value.astimezone(IST)

    def get_current_time(self):
        return datetime.now(IST)

    def calculate_required_energy(
        self,
        current_soc,
        target_soc
    ):

        difference = max(
            0.0,
            float(target_soc) - float(current_soc)
        )

        energy = (
            self.battery_capacity_kwh
            * difference
            / 100.0
        )

        return round(energy, 3)

    def calculate_charging_time(
        self,
        required_energy,
        charging_current=None
    ):

        # If a current is supplied, calculate the
        # actual charger power from 230 V.
        if charging_current is not None:

            charging_current = max(
                0.0,
                float(charging_current)
            )

            effective_power = (
                230.0
                * charging_current
                / 1000.0
            ) * 0.90

        else:

            effective_power = (
                self.charger_power_kw
                * 0.90
            )

        if effective_power <= 0:
            return 0.0

        hours = (
            float(required_energy)
            / effective_power
        )

        return round(
            hours * 60.0,
            1
        )

    def calculate_deadline_pressure(
        self,
        required_minutes,
        available_minutes
    ):

        if available_minutes <= 0:
            return "CRITICAL"

        ratio = (
            float(required_minutes)
            / float(available_minutes)
        )

        if ratio >= 1.0:
            return "CRITICAL"

        elif ratio >= 0.75:
            return "HIGH"

        elif ratio >= 0.45:
            return "MEDIUM"

        else:
            return "LOW"

    def create_schedule(
        self,
        current_soc,
        target_soc,
        departure_time,
        current_time=None,
        charging_current=None
    ):

        current_time = self.normalize_time(
            current_time
        )

        departure_time = self.normalize_time(
            departure_time
        )

        required_energy = (
            self.calculate_required_energy(
                current_soc,
                target_soc
            )
        )

        charging_minutes = (
            self.calculate_charging_time(
                required_energy,
                charging_current
            )
        )

        available_minutes = (
            departure_time - current_time
        ).total_seconds() / 60.0

        available_minutes = max(
            0.0,
            available_minutes
        )

        if charging_minutes <= available_minutes:

            schedule_status = "ON_TIME"

            latest_start = (
                departure_time
                - timedelta(
                    minutes=charging_minutes
                )
            )

        else:

            schedule_status = (
                "INSUFFICIENT_TIME"
            )

            latest_start = current_time

        deadline_pressure = (
            self.calculate_deadline_pressure(
                charging_minutes,
                available_minutes
            )
        )

        return {

            "current_time":
                current_time,

            "departure_time":
                departure_time,

            "current_soc":
                round(
                    float(current_soc),
                    2
                ),

            "target_soc":
                round(
                    float(target_soc),
                    2
                ),

            "required_energy_kwh":
                required_energy,

            "estimated_charging_minutes":
                charging_minutes,

            "available_minutes":
                round(
                    available_minutes,
                    1
                ),

            "latest_start_time":
                latest_start,

            "status":
                schedule_status,

            "deadline_pressure":
                deadline_pressure,

            "estimated_current":
                (
                    round(
                        float(charging_current),
                        2
                    )
                    if charging_current
                    is not None
                    else None
                )
        }