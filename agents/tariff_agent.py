from services.tariff_service import TariffService


class TariffAgent:

    def __init__(self):

        self.tariff_service = TariffService()

    # -------------------------------------

    def analyze(
            self,
            current_units,
            charging_units,
            current_hour
    ):

        total_units = current_units + charging_units

        rate = self.tariff_service.get_slab_rate(
            total_units
        )

        multiplier = self.tariff_service.get_tod_multiplier(
            current_hour
        )

        final_rate = rate * multiplier

        decision = {

            "current_units": current_units,

            "charging_units": charging_units,

            "total_units": total_units,

            "base_rate": rate,

            "tod_multiplier": multiplier,

            "final_rate": round(final_rate, 2)

        }

        return decision