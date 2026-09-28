from datetime import datetime


class TariffService:

    # Simulation tariff model
    # Keep these values configurable for your project.
    TARIFFS = {
        "PEAK": 9.75,
        "SOLAR": 6.50,
        "NORMAL": 8.10,
        "NIGHT": 8.10
    }

    def __init__(self):
        self.last_result = None

    # ---------------------------------------------------------
    # TIME-OF-DAY PERIOD
    # ---------------------------------------------------------

    def get_period(self, hour):

        if 6 <= hour < 9:
            return "PEAK"

        elif 9 <= hour < 16:
            return "SOLAR"

        elif 16 <= hour < 18:
            return "NORMAL"

        elif 18 <= hour < 22:
            return "PEAK"

        else:
            return "NIGHT"

    # ---------------------------------------------------------
    # SLAB RATE
    # ---------------------------------------------------------

    def get_slab_rate(self, total_units):

        total_units = float(total_units)

        # Slab structure for the simulation.
        if total_units <= 100:
            return 4.50

        elif total_units <= 200:
            return 5.50

        elif total_units <= 400:
            return 7.00

        elif total_units <= 500:
            return 8.50

        else:
            return 9.50

    # ---------------------------------------------------------
    # TIME-OF-DAY MULTIPLIER
    # ---------------------------------------------------------

    def get_tod_multiplier(self, current_hour):

        period = self.get_period(current_hour)

        if period == "PEAK":
            return 1.20

        elif period == "SOLAR":
            return 0.85

        elif period == "NIGHT":
            return 0.90

        return 1.00

    # ---------------------------------------------------------
    # FINAL RATE
    # ---------------------------------------------------------

    def get_rate(self, hour, total_units=0):

        slab_rate = self.get_slab_rate(total_units)

        multiplier = self.get_tod_multiplier(hour)

        final_rate = slab_rate * multiplier

        return round(final_rate, 2)

    # ---------------------------------------------------------
    # COST CALCULATION
    # ---------------------------------------------------------

    def calculate_cost(
        self,
        energy_kwh,
        hour,
        total_units=0
    ):

        period = self.get_period(hour)

        slab_rate = self.get_slab_rate(total_units)

        multiplier = self.get_tod_multiplier(hour)

        final_rate = slab_rate * multiplier

        cost = energy_kwh * final_rate

        result = {
            "energy_kwh": round(float(energy_kwh), 4),
            "period": period,
            "slab_rate": round(slab_rate, 2),
            "tod_multiplier": round(multiplier, 2),
            "final_rate": round(final_rate, 2),
            "cost": round(cost, 2)
        }

        self.last_result = result

        return result