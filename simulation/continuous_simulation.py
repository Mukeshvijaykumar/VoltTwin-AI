from simulation.battery import Battery
from simulation.virtual_charger import VirtualCharger

from agents.battery_agent import BatteryAgent
from agents.grid_agent import GridAgent
from agents.solar_agent import SolarAgent
from agents.tariff_agent import TariffAgent
from agents.user_agent import UserAgent
from agents.coordinator_agent import CoordinatorAgent

from services.weather_service import WeatherService
from services.grid_service import GridService

# -----------------------------------------
# INITIALIZE DIGITAL TWIN
# -----------------------------------------

battery = Battery(
    soc=42,
    temperature=37,
    health=96,
    charging_current=0
)

charger = VirtualCharger()

weather_service = WeatherService()
grid_service = GridService()

# -----------------------------------------
# INITIALIZE AI AGENTS
# -----------------------------------------

battery_agent = BatteryAgent()
grid_agent = GridAgent()
solar_agent = SolarAgent()
tariff_agent = TariffAgent()
user_agent = UserAgent()
coordinator = CoordinatorAgent()


# -----------------------------------------
# SIMULATION SETTINGS
# -----------------------------------------

target_soc = 90

current_units = 240

charging_units = 60

current_hour = 19


print("=" * 60)
print("CONTINUOUS EV CHARGING SIMULATION")
print("=" * 60)


# -----------------------------------------
# CONTINUOUS LOOP
# -----------------------------------------

step = 1

while battery.soc < target_soc:

    print("\n")
    print("-" * 60)
    print(f"SIMULATION STEP {step}")
    print("-" * 60)

    print("\nBattery Status:")
    print(battery.get_status())

    #get real time weather
    weather = weather_service.get_weather()

    temperature = weather["temperature"]
    humidity = weather["humidity"]
    cloud_cover = weather["cloud_cover"]
    wind_speed = weather["wind_speed"]
    print("LIVE WEATHER")
    print(weather)

    # -------------------------------------
# GET GRID DATA
# -------------------------------------

    grid = grid_service.get_grid_status()
    print("LIVE GRID")
    print("\nLIVE GRID DATA:")
    print(grid)

    # -------------------------------------
    # AGENT ANALYSIS
    # -------------------------------------

    battery_result = battery_agent.analyze(battery)

    grid_result = grid_agent.analyze(grid)

    solar_result = solar_agent.analyze(
        cloud_cover
    )

    tariff_result = tariff_agent.analyze(
        current_units,
        charging_units,
        current_hour
    )

    user_result = user_agent.analyze(
        battery.soc,
        target_soc
    )


    # -------------------------------------
    # COORDINATOR DECISION
    # -------------------------------------

    decision = coordinator.decide(

        battery_result,
        tariff_result,
        solar_result,
        grid_result,
        user_result
    )


    print("\nAI Decision:")
    print(decision)


    # -------------------------------------
    # VIRTUAL CHARGER
    # -------------------------------------

    charger_status = charger.execute(
        decision
    )
    battery.charging_current = charger_status["current"]

    print("\nVirtual Charger:")
    print(charger_status)


    # -------------------------------------
    # DIGITAL TWIN UPDATE
    # -------------------------------------

    if charger_status["status"] == "CHARGING":

        battery.charge(

            charger_status["current"],

            duration_minutes=10

        )

    else:

        print("\nCharging not active.")
        break


    # -------------------------------------
    # UPDATE TIME
    # -------------------------------------

    current_hour += 1

    if current_hour >= 24:

        current_hour = 0


    step += 1


# -----------------------------------------
# FINAL RESULT
# -----------------------------------------

print("\n")
print("=" * 60)
print("SIMULATION COMPLETED")
print("=" * 60)

print("\nFinal Battery Status:")

print(battery.get_status())

print(f"\nTarget SOC: {target_soc}%")

print("=" * 60)