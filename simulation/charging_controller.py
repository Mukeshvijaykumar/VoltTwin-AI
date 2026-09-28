from datetime import datetime, timedelta

from simulation.battery import Battery
from simulation.virtual_charger import VirtualCharger

from agents.battery_agent import BatteryAgent
from agents.grid_agent import GridAgent
from agents.solar_agent import SolarAgent
from agents.tariff_agent import TariffAgent
from agents.user_agent import UserAgent
from agents.coordinator_agent import CoordinatorAgent

from services.weather_service import WeatherService
from services.tariff_service import TariffService
from services.location_service import LocationService
from services.grid_manager import GridManager
from services.charging_scheduler import ChargingScheduler


class ChargingController:

    def __init__(
        self,
        target_soc=80.0,
        departure_time=None
    ):

        # --------------------------------------------------
        # USER REQUIREMENT
        # --------------------------------------------------

        self.target_soc = float(target_soc)
        self.departure_time = departure_time

        # --------------------------------------------------
        # DIGITAL TWIN BATTERY
        # --------------------------------------------------

        self.battery = Battery(
            soc=42.0,
            temperature=37.0,
            health=96.0,
            capacity_kwh=40.0,
            current=0.0
        )

        # --------------------------------------------------
        # VIRTUAL CHARGER
        # --------------------------------------------------

        self.charger = VirtualCharger()

        # --------------------------------------------------
        # SERVICES
        # --------------------------------------------------

        self.weather_service = WeatherService()
        self.tariff_service = TariffService()
        self.location_service = LocationService()
        self.grid_manager = GridManager()

        self.scheduler = ChargingScheduler(
            battery_capacity_kwh=40.0,
            charger_power_kw=7.36
        )

        # --------------------------------------------------
        # AI AGENTS
        # --------------------------------------------------

        self.battery_agent = BatteryAgent()
        self.grid_agent = GridAgent()
        self.solar_agent = SolarAgent()
        self.tariff_agent = TariffAgent()
        self.user_agent = UserAgent()

        self.coordinator = CoordinatorAgent()

        # --------------------------------------------------
        # SIMULATION CLOCK
        # --------------------------------------------------

        self.simulation_time = datetime.now()

        # One controller cycle = one simulated minute
        self.simulation_minutes_per_cycle = 1

        self.total_simulation_minutes = 0

        # --------------------------------------------------
        # CONTROLLER STATE
        # --------------------------------------------------

        self.step = 0

        self.total_energy_kwh = 0.0
        self.total_cost = 0.0

        self.cooling_cycles = 0
        self.restart_count = 0

        self.was_cooling = False
        self.completed = False

        self.last_location = None
        self.last_weather = None
        self.last_grid = None
        self.last_schedule = None
        self.last_decision = None
        self.last_charger = None
        self.last_record = None

    # ======================================================
    # LOCATION
    # ======================================================

    def get_location(self, latitude, longitude):

        try:

            location = self.location_service.reverse_geocode(
                latitude,
                longitude
            )

            self.last_location = location

            return location

        except Exception:

            location = {
                "latitude": float(latitude),
                "longitude": float(longitude),
                "locality": "Unknown",
                "city": "",
                "district": "",
                "state": "Tamil Nadu",
                "country": "India",
                "postcode": "",
                "display_name": "Current Location",
                "source": "Location Fallback",
                "is_live": False
            }

            self.last_location = location

            return location

    # ======================================================
    # WEATHER
    # ======================================================

    def get_weather(
        self,
        latitude,
        longitude,
        location_name="Current Location"
    ):

        try:

            weather = self.weather_service.get_weather(
                latitude,
                longitude,
                location_name
            )

            self.last_weather = weather

            return weather

        except Exception:

            weather = {
                "temperature": 30.0,
                "apparent_temperature": 30.0,
                "humidity": 60.0,
                "precipitation": 0.0,
                "rain": 0.0,
                "cloud_cover": 50.0,
                "wind_speed": 10.0,
                "wind_direction": 0.0,
                "timestamp": self.simulation_time.isoformat(),
                "latitude": latitude,
                "longitude": longitude,
                "location": location_name,
                "source": "Weather Fallback",
                "is_live": False
            }

            self.last_weather = weather

            return weather

    # ======================================================
    # ENERGY CALCULATION
    # ======================================================

    def calculate_energy(
        self,
        current,
        duration_minutes
    ):

        voltage = self.battery.get_voltage()

        power_kw = (
            voltage * current
        ) / 1000.0

        energy = (
            power_kw
            * duration_minutes
            / 60.0
        )

        return round(energy, 4)

    # ======================================================
    # SCHEDULING
    # ======================================================

    def create_schedule(self):

        if self.departure_time is None:
            return None

        schedule = self.scheduler.create_schedule(
            current_soc=self.battery.soc,
            target_soc=self.target_soc,
            departure_time=self.departure_time,
            current_time=self.simulation_time
        )

        self.last_schedule = schedule

        return schedule

    # ======================================================
    # SIMULATION CLOCK
    # ======================================================

    def advance_simulation_time(self):

        minutes = self.simulation_minutes_per_cycle

        self.simulation_time += timedelta(
            minutes=minutes
        )

        self.total_simulation_minutes += minutes

    # ======================================================
    # MAIN CONTROLLER CYCLE
    # ======================================================

    def run_cycle(
        self,
        latitude,
        longitude
    ):

        self.step += 1

        simulation_minutes = (
            self.simulation_minutes_per_cycle
        )

        # --------------------------------------------------
        # LOCATION
        # --------------------------------------------------

        location = self.get_location(
            latitude,
            longitude
        )

        locality = location.get(
            "locality",
            "Unknown"
        )

        district = location.get(
            "district",
            "Unknown"
        )

        # --------------------------------------------------
        # WEATHER
        # --------------------------------------------------

        weather = self.get_weather(
            latitude,
            longitude,
            location.get(
                "display_name",
                locality
            )
        )

        # --------------------------------------------------
        # GRID
        # --------------------------------------------------

        try:

            grid = self.grid_manager.get_grid_status(
                latitude,
                longitude,
                locality,
                district
            )

        except Exception:

            grid = {
                "grid_load": 65.0,
                "demand_mw": None,
                "capacity_mw": 100.0,
                "status": "NORMAL",
                "source": "Grid Fallback",
                "is_live": False,
                "is_estimated": True,
                "timestamp": self.simulation_time.isoformat()
            }

        self.last_grid = grid

        # --------------------------------------------------
        # CURRENT SIMULATION HOUR
        # --------------------------------------------------

        current_hour = self.simulation_time.hour

        # --------------------------------------------------
        # TARGET ALREADY REACHED
        # --------------------------------------------------

        if self.battery.soc >= self.target_soc:

            self.completed = True

            decision = {
                "action": "STOP_CHARGING",
                "current": 0.0,
                "mode": "COMPLETED",
                "reason": "Target SOC reached"
            }

            charger_status = self.charger.execute(
                decision
            )

            self.last_decision = decision
            self.last_charger = charger_status

            record = self._record(
                location=location,
                weather=weather,
                grid=grid,
                schedule=self.last_schedule,
                decision=decision,
                charger_status=charger_status,
                current=0.0,
                energy=0.0,
                cost=0.0,
                status="COMPLETED"
            )

            self.advance_simulation_time()

            return record

        # --------------------------------------------------
        # SCHEDULE
        # --------------------------------------------------

        schedule = self.create_schedule()

        # --------------------------------------------------
        # DEADLINE CHECK
        # --------------------------------------------------

        deadline_missed = False

        if self.departure_time is not None:

            if (
                self.simulation_time
                >= self.departure_time
                and
                self.battery.soc
                < self.target_soc
            ):

                deadline_missed = True

        if deadline_missed:

            decision = {
                "action": "STOP_CHARGING",
                "current": 0.0,
                "mode": "DEADLINE_MISSED",
                "reason": (
                    "Departure deadline reached "
                    "before target SOC"
                )
            }

            charger_status = self.charger.execute(
                decision
            )

            self.last_decision = decision
            self.last_charger = charger_status

            record = self._record(
                location=location,
                weather=weather,
                grid=grid,
                schedule=schedule,
                decision=decision,
                charger_status=charger_status,
                current=0.0,
                energy=0.0,
                cost=0.0,
                status="DEADLINE_MISSED"
            )

            self.advance_simulation_time()

            return record

        # --------------------------------------------------
        # THERMAL SAFETY
        # --------------------------------------------------

        temperature = self.battery.temperature

        # Critical temperature
        if temperature >= 48.0:

            self.cooling_cycles += 1
            self.was_cooling = True

            decision = {
                "action": "WAIT",
                "current": 0.0,
                "mode": "COOLING",
                "reason": (
                    "Battery temperature critical - "
                    "charging temporarily suspended"
                )
            }

            charger_status = self.charger.execute(
                decision
            )

            # One simulated minute of cooling
            self.battery.cool_down(
                simulation_minutes
            )

            self.last_decision = decision
            self.last_charger = charger_status

            record = self._record(
                location=location,
                weather=weather,
                grid=grid,
                schedule=schedule,
                decision=decision,
                charger_status=charger_status,
                current=0.0,
                energy=0.0,
                cost=0.0,
                status="COOLING"
            )

            self.advance_simulation_time()

            return record

        # --------------------------------------------------
        # HIGH TEMPERATURE
        # --------------------------------------------------

        if temperature >= 45.0:

            self.cooling_cycles += 1
            self.was_cooling = True

            decision = {
                "action": "WAIT",
                "current": 0.0,
                "mode": "COOLING",
                "reason": (
                    "Battery temperature high - "
                    "cooling before charging resumes"
                )
            }

            charger_status = self.charger.execute(
                decision
            )

            self.battery.cool_down(
                simulation_minutes
            )

            self.last_decision = decision
            self.last_charger = charger_status

            record = self._record(
                location=location,
                weather=weather,
                grid=grid,
                schedule=schedule,
                decision=decision,
                charger_status=charger_status,
                current=0.0,
                energy=0.0,
                cost=0.0,
                status="COOLING"
            )

            self.advance_simulation_time()

            return record

        # --------------------------------------------------
        # COOLING RECOVERY
        # --------------------------------------------------

        if self.was_cooling:

            self.restart_count += 1
            self.was_cooling = False

        # --------------------------------------------------
        # AGENT DECISIONS
        # --------------------------------------------------

        battery_decision = self.battery_agent.analyze(
            self.battery
        )

        grid_decision = self.grid_agent.analyze(
            grid
        )

        cloud_cover = weather.get(
            "cloud_cover",
            50.0
        )

        solar_decision = self.solar_agent.analyze(
            cloud_cover
        )

        # --------------------------------------------------
        # TARIFF
        # --------------------------------------------------

        current_units = 240.0
        charging_units = 60.0

        tariff_decision = self.tariff_agent.analyze(
            current_units,
            charging_units,
            current_hour
        )

        # --------------------------------------------------
        # USER
        # --------------------------------------------------

        user_decision = self.user_agent.analyze(
            self.battery.soc,
            self.target_soc
        )

        # --------------------------------------------------
        # COORDINATOR
        # --------------------------------------------------

        decision = self.coordinator.decide(
            battery_decision=battery_decision,
            tariff_decision=tariff_decision,
            solar_decision=solar_decision,
            grid_decision=grid_decision,
            user_decision=user_decision,
            schedule=schedule
        )

        # --------------------------------------------------
        # SAFETY OVERRIDES
        # --------------------------------------------------

        requested_current = float(
            decision.get("current", 0.0)
        )

        mode = decision.get(
            "mode",
            "IDLE"
        )

        reason = decision.get(
            "reason",
            ""
        )

        action = decision.get(
            "action",
            "WAIT"
        )

        grid_load = float(
            grid.get(
                "grid_load",
                65.0
            )
        )

        battery_temperature = (
            self.battery.temperature
        )

        # Battery safety
        if battery_decision.get("action") == "STOP":

            requested_current = 0.0
            action = "STOP_CHARGING"
            mode = "SAFETY_STOP"

            reason = (
                "Battery safety limit reached"
            )

        elif battery_decision.get("action") == "REDUCE":

            requested_current = min(
                requested_current,
                16.0
            )

            mode = "BATTERY_PROTECTED"

            reason = (
                "Charging current reduced "
                "due to battery condition"
            )

        # Grid safety
        if grid_load >= 90.0:

            requested_current = 0.0
            action = "WAIT"
            mode = "WAITING_GRID"

            reason = (
                "Grid load critical - "
                "charging postponed"
            )

        elif grid_load >= 75.0:

            requested_current = min(
                requested_current,
                16.0
            )

            if requested_current > 0:
                mode = "GRID_LIMITED"

            reason = (
                "Grid demand high - "
                "charging current limited"
            )

        # Battery thermal protection
        if battery_temperature >= 42.0:

            requested_current = min(
                requested_current,
                16.0
            )

            if requested_current > 0:
                mode = "THERMAL_LIMITED"

            reason = (
                "Battery temperature elevated - "
                "charging current limited"
            )

        # --------------------------------------------------
        # DEADLINE PRESSURE
        # --------------------------------------------------

        pressure = "LOW"

        if schedule:

            pressure = schedule.get(
                "deadline_pressure",
                "LOW"
            )

        # Deadline can increase current,
        # but NEVER override safety limits.

        if (
            pressure in ["HIGH", "CRITICAL"]
            and
            battery_temperature < 42.0
            and
            grid_load < 75.0
            and
            battery_decision.get("action")
            not in ["STOP", "REDUCE"]
        ):

            requested_current = 32.0
            mode = "FAST_CHARGING"

            reason = (
                "High deadline pressure - "
                "fast charging requested"
            )

        elif pressure == "MEDIUM":

            if requested_current > 0:

                requested_current = min(
                    requested_current,
                    24.0
                )

                mode = "NORMAL_CHARGING"

        elif pressure == "LOW":

            if requested_current > 0:

                requested_current = min(
                    requested_current,
                    16.0
                )

                mode = "SLOW_CHARGING"

        # --------------------------------------------------
        # USER TARGET
        # --------------------------------------------------

        if user_decision.get("action") == "READY":

            requested_current = 0.0
            action = "WAIT"
            mode = "TARGET_REACHED"

            reason = (
                "Target SOC already satisfied"
            )

        # --------------------------------------------------
        # FINAL ACTION
        # --------------------------------------------------

        if requested_current <= 0.0:

            if action == "START_CHARGING":
                action = "WAIT"

        else:

            action = "START_CHARGING"

        final_decision = {
            "action": action,
            "current": round(
                requested_current,
                2
            ),
            "mode": mode,
            "reason": reason
        }

        # --------------------------------------------------
        # CHARGER
        # --------------------------------------------------

        charger_status = self.charger.execute(
            final_decision
        )

        # --------------------------------------------------
        # BATTERY CHARGING
        # --------------------------------------------------

        energy = 0.0
        cost = 0.0

        if requested_current > 0:

            before_soc = self.battery.soc

            self.battery.charge(
                requested_current,
                simulation_minutes
            )

            after_soc = self.battery.soc

            energy = self.calculate_energy(
                requested_current,
                simulation_minutes
            )

            energy = max(
                0.0,
                energy
            )

            # Actual battery energy
            battery_energy = max(
                0.0,
                (
                    after_soc - before_soc
                )
                * self.battery.capacity_kwh
                / 100.0
            )

            self.total_energy_kwh += (
                battery_energy
            )

            # --------------------------------------------------
            # COST
            # --------------------------------------------------

            total_units = (
                240.0
                +
                self.total_energy_kwh
            )

            cost_data = (
                self.tariff_service.calculate_cost(
                    energy_kwh=battery_energy,
                    hour=current_hour,
                    total_units=total_units
                )
            )

            cost = cost_data.get(
                "cost",
                0.0
            )

            self.total_cost += cost

        # --------------------------------------------------
        # TARGET CHECK AFTER CHARGING
        # --------------------------------------------------

        status = "RUNNING"

        if self.battery.soc >= self.target_soc:

            self.battery.soc = min(
                self.battery.soc,
                100.0
            )

            self.completed = True

            status = "COMPLETED"

        # --------------------------------------------------
        # TELEMETRY RECORD
        # --------------------------------------------------

        record = self._record(
            location=location,
            weather=weather,
            grid=grid,
            schedule=schedule,
            decision=final_decision,
            charger_status=charger_status,
            current=requested_current,
            energy=energy,
            cost=cost,
            status=status
        )

        # --------------------------------------------------
        # ADVANCE SIMULATION CLOCK
        # --------------------------------------------------

        self.advance_simulation_time()

        return record

    # ======================================================
    # TELEMETRY
    # ======================================================

    def _record(
        self,
        location,
        weather,
        grid,
        schedule,
        decision,
        charger_status,
        current,
        energy,
        cost,
        status
    ):

        battery_status = self.battery.status()

        record = {

            # ----------------------------------------------
            # TIME
            # ----------------------------------------------

            "step": self.step,

            "simulation_time":
                self.simulation_time.isoformat(),

            "simulation_minutes":
                self.total_simulation_minutes,

            # ----------------------------------------------
            # LOCATION
            # ----------------------------------------------

            "latitude":
                location.get("latitude"),

            "longitude":
                location.get("longitude"),

            "locality":
                location.get("locality"),

            "city":
                location.get("city"),

            "district":
                location.get("district"),

            # ----------------------------------------------
            # WEATHER
            # ----------------------------------------------

            "weather_temperature":
                weather.get("temperature"),

            "humidity":
                weather.get("humidity"),

            "cloud_cover":
                weather.get("cloud_cover"),

            "rain":
                weather.get("rain"),

            "wind_speed":
                weather.get("wind_speed"),

            # ----------------------------------------------
            # GRID
            # ----------------------------------------------

            "grid_load":
                grid.get("grid_load"),

            "grid_status":
                grid.get("status"),

            "grid_source":
                grid.get("source"),

            "grid_is_live":
                grid.get("is_live", False),

            # ----------------------------------------------
            # BATTERY
            # ----------------------------------------------

            "SOC":
                battery_status.get("SOC"),

            "Temperature":
                battery_status.get(
                    "Temperature"
                ),

            "Health":
                battery_status.get(
                    "Health"
                ),

            "Voltage":
                battery_status.get(
                    "Voltage"
                ),

            "Battery_Current":
                battery_status.get(
                    "Current"
                ),

            "Battery_Power_kW":
                battery_status.get(
                    "Power_kW"
                ),

            "Battery_Energy_kWh":
                battery_status.get(
                    "Energy_kWh"
                ),

            "Capacity_kWh":
                battery_status.get(
                    "Capacity_kWh"
                ),

            # ----------------------------------------------
            # CHARGER
            # ----------------------------------------------

            "Charger_Current":
                charger_status.get(
                    "current",
                    0.0
                ),

            "Charger_Voltage":
                charger_status.get(
                    "voltage",
                    230.0
                ),

            "Charger_Power_kW":
                charger_status.get(
                    "power_kw",
                    0.0
                ),

            "Charger_Status":
                charger_status.get(
                    "status",
                    "IDLE"
                ),

            "Charging_Mode":
                charger_status.get(
                    "mode",
                    "IDLE"
                ),

            # ----------------------------------------------
            # AI DECISION
            # ----------------------------------------------

            "Action":
                decision.get(
                    "action"
                ),

            "Decision_Current":
                decision.get(
                    "current",
                    0.0
                ),

            "Decision_Mode":
                decision.get(
                    "mode"
                ),

            "Decision_Reason":
                decision.get(
                    "reason"
                ),

            # ----------------------------------------------
            # SCHEDULE
            # ----------------------------------------------

            "Target_SOC":
                self.target_soc,

            "Departure_Time":
                (
                    self.departure_time.isoformat()
                    if self.departure_time
                    else None
                ),

            "Deadline_Pressure":
                (
                    schedule.get(
                        "deadline_pressure"
                    )
                    if schedule
                    else "NONE"
                ),

            "Required_Energy_kWh":
                (
                    schedule.get(
                        "required_energy_kwh"
                    )
                    if schedule
                    else None
                ),

            "Estimated_Charging_Minutes":
                (
                    schedule.get(
                        "estimated_charging_minutes"
                    )
                    if schedule
                    else None
                ),

            "Available_Minutes":
                (
                    schedule.get(
                        "available_minutes"
                    )
                    if schedule
                    else None
                ),

            # ----------------------------------------------
            # ENERGY / COST
            # ----------------------------------------------

            "Cycle_Energy_kWh":
                round(energy, 4),

            "Cycle_Cost":
                round(cost, 2),

            "Total_Energy_kWh":
                round(
                    self.total_energy_kwh,
                    4
                ),

            "Total_Cost":
                round(
                    self.total_cost,
                    2
                ),

            # ----------------------------------------------
            # THERMAL
            # ----------------------------------------------

            "Cooling":
                status == "COOLING",

            "Cooling_Cycles":
                self.cooling_cycles,

            "Restart_Count":
                self.restart_count,

            # ----------------------------------------------
            # STATUS
            # ----------------------------------------------

            "Status":
                status,

            "Completed":
                self.completed
        }

        self.last_record = record

        return record

    # ======================================================
    # CURRENT STATUS
    # ======================================================

    def get_status(self):

        return {

            "step":
                self.step,

            "simulation_time":
                self.simulation_time,

            "total_simulation_minutes":
                self.total_simulation_minutes,

            "battery":
                self.battery.status(),

            "charger":
                self.charger.get_status(),

            "target_soc":
                self.target_soc,

            "departure_time":
                self.departure_time,

            "total_energy_kwh":
                round(
                    self.total_energy_kwh,
                    4
                ),

            "total_cost":
                round(
                    self.total_cost,
                    2
                ),

            "cooling_cycles":
                self.cooling_cycles,

            "restart_count":
                self.restart_count,

            "completed":
                self.completed
        }