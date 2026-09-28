from datetime import datetime

# ==============================
# Digital Twin Imports
# ==============================
from digital_twin.battery import Battery
from digital_twin.charger import Charger

# ==============================
# Agent Imports
# ==============================
from agents.battery_agent import BatteryAgent
from agents.tariff_agent import TariffAgent
from agents.solar_agent import SolarAgent
from agents.grid_agent import GridAgent
from agents.user_agent import UserAgent
from agents.coordinator_agent import CoordinatorAgent

# ==============================
# Service Imports
# ==============================
from services.weather_service import WeatherService
from services.grid_service import GridService
from services.user_service import UserService


# ====================================================
# CREATE DIGITAL TWIN OBJECTS
# ====================================================

battery = Battery(
    capacity=40,
    soc=60,
    temperature=43,
    health=98
)

charger = Charger(battery)


# ====================================================
# CREATE AGENTS
# ====================================================

battery_agent = BatteryAgent()
tariff_agent = TariffAgent()
solar_agent = SolarAgent()
grid_agent = GridAgent()
user_agent = UserAgent()
coordinator = CoordinatorAgent()


# ====================================================
# CREATE SERVICES
# ====================================================

weather_service = WeatherService()
grid_service = GridService()
user_service = UserService()


# ====================================================
# BATTERY AGENT
# ====================================================

battery_decision = battery_agent.analyze(battery)

print("\n========== Battery Agent ==========")
print(battery_decision)


# ====================================================
# TARIFF AGENT
# ====================================================

current_hour = datetime.now().hour

monthly_units = 185

tariff_decision = tariff_agent.analyze(
    current_hour,
    monthly_units
)
print("\n========== Tariff Agent ==========")
print(tariff_decision)


# ====================================================
# WEATHER SERVICE
# ====================================================

weather = weather_service.get_weather()

print("\n========== Weather ==========")
print(weather)


# ====================================================
# SOLAR AGENT
# ====================================================

solar_decision = solar_agent.analyze(
    weather["cloud_cover"]
)

print("\n========== Solar Agent ==========")
print(solar_decision)


# ====================================================
# GRID SERVICE
# ====================================================

grid = grid_service.get_grid_load()

print("\n========== Grid ==========")
print(grid)


# ====================================================
# GRID AGENT
# ====================================================

grid_decision = grid_agent.analyze(
    grid["grid_load"]
)

print("\n========== Grid Agent ==========")
print(grid_decision)


# ====================================================
# USER SERVICE
# ====================================================

user_data = user_service.get_user_requirement()

print("\n========== User Requirement ==========")
print(user_data)


# ====================================================
# USER AGENT
# ====================================================

user_decision = user_agent.analyze(
    battery.soc,
    user_data["required_soc"]
)

print("\n========== User Agent ==========")
print(user_decision)


# ====================================================
# COORDINATOR AGENT
# ====================================================

final_decision = coordinator.decide(
    battery_decision,
    tariff_decision,
    solar_decision,
    grid_decision,
    user_decision
)

print("\n========== Final Decision ==========")
print(final_decision)


# ====================================================
# VIRTUAL CHARGER
# ====================================================

if final_decision["action"] == "START_CHARGING":
    charger.start(final_decision["current"])
else:
    charger.stop()


# ====================================================
# FINAL STATUS
# ====================================================

print("\n========== Charger ==========")
print("Status  :", charger.status)
print("Current :", charger.current)

print("\n========== Battery ==========")
print("SOC         :", battery.soc)
print("Temperature :", battery.temperature)
print("Charging    :", battery.is_charging)