from datetime import datetime
import zoneinfo
import math

IST = zoneinfo.ZoneInfo("Asia/Kolkata")

class LocalGridService:

    def __init__(self):

        self.reference_capacity_mw = 100.0

    def get_grid_status(
        self,
        latitude,
        longitude,
        locality="Unknown",
        district="Unknown"
    ):

        now = datetime.now(IST)

        hour = now.hour

        weekday = now.weekday()

        # ---------------------------------
        # LOCATION LOAD FACTOR
        # ---------------------------------

        location_factor = (
            self.get_location_factor(
                latitude,
                longitude,
                locality,
                district
            )
        )

        # ---------------------------------
        # TIME-OF-DAY LOAD
        # ---------------------------------

        time_factor = (
            self.get_time_factor(
                hour
            )
        )

        # ---------------------------------
        # WEEKDAY / WEEKEND
        # ---------------------------------

        if weekday >= 5:

            day_factor = 0.88

        else:

            day_factor = 1.0

        # ---------------------------------
        # COMBINE
        # ---------------------------------

        base_load = (
            65 *
            time_factor *
            location_factor *
            day_factor
        )

        # ---------------------------------
        # NATURAL VARIATION
        # ---------------------------------

        variation = (
            3 *
            math.sin(
                now.minute / 60 * 2 * math.pi
            )
        )

        grid_load = (
            base_load +
            variation
        )

        grid_load = max(
            30,
            min(
                98,
                grid_load
            )
        )

        grid_load = round(
            grid_load,
            2
        )

        # ---------------------------------
        # DEMAND
        # ---------------------------------

        demand_mw = round(
            (
                grid_load / 100
            ) *
            self.reference_capacity_mw,
            2
        )

        if grid_load >= 90:

            status = "CRITICAL"

        elif grid_load >= 75:

            status = "HIGH"

        elif grid_load >= 55:

            status = "NORMAL"

        else:

            status = "LOW"

        return {

            "grid_load":
                grid_load,

            "demand_mw":
                demand_mw,

            "capacity_mw":
                self.reference_capacity_mw,

            "hour":
                hour,

            "locality":
                locality,

            "district":
                district,

            "status":
                status,

            "source":
                "Location-Aware Grid Simulation",

            "is_live":
                False,

            "is_estimated":
                True,

            "timestamp":
                now.isoformat()
        }

    def get_location_factor(
        self,
        latitude,
        longitude,
        locality,
        district
    ):

        name = (
            f"{locality} {district}"
        ).lower()

        # Chennai metropolitan areas
        if any(
            word in name
            for word in [
                "porur",
                "tambaram",
                "chennai",
                "guindy",
                "ambattur",
                "avadi",
                "velachery",
                "chromepet",
                "pallavaram",
                "medavakkam",
                "sholinganallur"
            ]
        ):

            return 1.10

        # Coimbatore region
        if any(
            word in name
            for word in [
                "coimbatore",
                "pollachi",
                "anaimalai",
                "tiruppur"
            ]
        ):

            return 0.92

        # Industrial areas
        if any(
            word in name
            for word in [
                "hosur",
                "sriperumbudur",
                "oragadam",
                "ranipet",
                "salem"
            ]
        ):

            return 1.05

        # Rural / lower-density areas
        if any(
            word in name
            for word in [
                "village",
                "rural"
            ]
        ):

            return 0.78

        return 0.95

    def get_time_factor(self, hour):

        # 00:00 - 05:00
        if 0 <= hour < 6:

            return 0.72

        # 06:00 - 09:00
        if 6 <= hour < 9:

            return 0.95

        # 09:00 - 16:00
        if 9 <= hour < 16:

            return 0.82

        # 16:00 - 18:00
        if 16 <= hour < 18:

            return 1.00

        # 18:00 - 22:00
        if 18 <= hour < 22:

            return 1.25

        # 22:00 - midnight
        return 0.90