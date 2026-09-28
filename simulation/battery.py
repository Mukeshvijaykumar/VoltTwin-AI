class Battery:

    def __init__(
        self,
        soc=42.0,
        temperature=37.0,
        health=96.0,
        capacity_kwh=40.0,
        current=0.0
    ):
        self.soc = float(soc)
        self.temperature = float(temperature)
        self.health = float(health)

        self.capacity_kwh = float(capacity_kwh)

        self.nominal_voltage = 230.0
        self.current = float(current)

        self.efficiency = 0.90

        self.last_power_kw = 0.0
        self.last_energy_kwh = 0.0

    # --------------------------------------------------
    # BATTERY VOLTAGE MODEL
    # --------------------------------------------------

    def get_voltage(self):

        if self.soc < 20:
            return 210.0

        elif self.soc < 40:
            return 220.0

        elif self.soc < 60:
            return 230.0

        elif self.soc < 80:
            return 235.0

        elif self.soc < 90:
            return 240.0

        else:
            return 245.0

    # --------------------------------------------------
    # SOC CHARGING TAPER
    # --------------------------------------------------

    def get_soc_charge_factor(self):

        if self.soc < 70:
            return 1.00

        elif self.soc < 80:
            return 0.95

        elif self.soc < 90:
            return 0.75

        elif self.soc < 95:
            return 0.50

        else:
            return 0.25

    # --------------------------------------------------
    # TEMPERATURE LIMIT
    # --------------------------------------------------

    def get_temperature_current_limit(self):

        if self.temperature < 40:
            return 32.0

        elif self.temperature < 42:
            return 24.0

        elif self.temperature < 45:
            return 16.0

        elif self.temperature < 48:
            return 8.0

        else:
            return 0.0

    # --------------------------------------------------
    # CHARGE
    # --------------------------------------------------

    def charge(self, requested_current, duration_minutes):

        requested_current = max(
            0.0,
            float(requested_current)
        )

        duration_minutes = max(
            0.0,
            float(duration_minutes)
        )

        if self.soc >= 100:
            self.current = 0.0
            self.last_power_kw = 0.0
            self.last_energy_kwh = 0.0
            return self.status()

        # Battery thermal limit
        thermal_limit = self.get_temperature_current_limit()

        # SOC taper
        soc_factor = self.get_soc_charge_factor()

        # Maximum accepted current
        accepted_current = min(
            requested_current,
            32.0,
            thermal_limit
        )

        accepted_current *= soc_factor

        accepted_current = max(
            0.0,
            accepted_current
        )

        voltage = self.get_voltage()

        power_kw = (
            voltage *
            accepted_current /
            1000.0
        )

        input_energy = (
            power_kw *
            duration_minutes /
            60.0
        )

        battery_energy = (
            input_energy *
            self.efficiency
        )

        soc_increase = (
            battery_energy /
            self.capacity_kwh
        ) * 100.0

        self.soc += soc_increase

        self.soc = min(
            100.0,
            self.soc
        )

        # Thermal model
        temperature_increase = (
            accepted_current *
            duration_minutes *
            0.002
        )

        self.temperature += temperature_increase

        self.current = accepted_current
        self.last_power_kw = power_kw
        self.last_energy_kwh = battery_energy

        return self.status()

    # --------------------------------------------------
    # COOLING
    # --------------------------------------------------

    def cool_down(self, duration_minutes=10):

        duration_minutes = max(
            0.0,
            float(duration_minutes)
        )

        cooling_rate = 0.08

        temperature_decrease = (
            cooling_rate *
            duration_minutes
        )

        self.temperature -= temperature_decrease

        self.temperature = max(
            30.0,
            self.temperature
        )

        self.current = 0.0
        self.last_power_kw = 0.0
        self.last_energy_kwh = 0.0

        return self.status()

    # --------------------------------------------------
    # STATUS
    # --------------------------------------------------

    def status(self):

        return {
            "SOC": round(self.soc, 2),
            "Temperature": round(
                self.temperature,
                2
            ),
            "Health": round(
                self.health,
                2
            ),
            "Voltage": round(
                self.get_voltage(),
                2
            ),
            "Current": round(
                self.current,
                2
            ),
            "Power_kW": round(
                self.last_power_kw,
                3
            ),
            "Energy_kWh": round(
                self.last_energy_kwh,
                4
            ),
            "Capacity_kWh": round(
                self.capacity_kwh,
                2
            )
        }
    @property
    def charging_current(self):
        return self.current
    def get_status(self):
        return self.status()