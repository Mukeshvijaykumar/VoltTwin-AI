class ChargingCostService:

    def __init__(self, voltage=400, tariff_per_kwh=8.0):

        self.voltage = voltage
        self.tariff_per_kwh = tariff_per_kwh
        self.total_energy_kwh = 0.0
        self.total_cost = 0.0

    def calculate_step_cost(self, current, duration_minutes):

        if current <= 0:
            return {
                "energy_kwh": 0.0,
                "cost": 0.0
            }

        energy_kwh = (
            self.voltage
            * current
            * (duration_minutes / 60)
            / 1000
        )

        cost = energy_kwh * self.tariff_per_kwh

        self.total_energy_kwh += energy_kwh
        self.total_cost += cost

        return {
            "energy_kwh": round(energy_kwh, 3),
            "cost": round(cost, 2)
        }

    def get_total_cost(self):

        return {
            "total_energy_kwh": round(
                self.total_energy_kwh, 3
            ),
            "total_cost": round(
                self.total_cost, 2
            )
        }