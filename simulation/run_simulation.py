from simulation.battery import Battery
from simulation.charging_history import ChargingHistory
from agents.battery_agent import BatteryAgent
from agents.grid_agent import GridAgent
from agents.solar_agent import SolarAgent
from agents.tariff_agent import TariffAgent
from agents.user_agent import UserAgent
from agents.coordinator_agent import CoordinatorAgent
battery = Battery()

battery_agent = BatteryAgent()
grid_agent = GridAgent()
solar_agent = SolarAgent()
tariff_agent = TariffAgent()
user_agent = UserAgent()
coordinator = CoordinatorAgent()

history = ChargingHistory()
print("="*60)
print("DIGITAL TWIN")
print("="*60)

print(battery.status())
grid = {

    "grid_load":82

}

cloud_cover = 55

current_units = 240

charging_units = 60

current_hour = 19

required_soc = 90
battery_result = battery_agent.analyze(battery)
grid_result = grid_agent.analyze(grid)
solar_result = solar_agent.analyze(cloud_cover)
tariff_result = tariff_agent.analyze(

    current_units,

    charging_units,

    current_hour

)
user_result = user_agent.analyze(

    battery.soc,

    required_soc

)
print()

print("Battery Agent")

print(battery_result)

print()

print("Grid Agent")

print(grid_result)

print()

print("Solar Agent")

print(solar_result)

print()

print("Tariff Agent")

print(tariff_result)

print()

print("User Agent")

print(user_result)
decision = coordinator.decide(

    battery_result,

    tariff_result,

    solar_result,

    grid_result,

    user_result

)
print()

print("="*60)

print("FINAL DECISION")

print("="*60)

print(decision)
battery.charge(

    decision["current"]

)
print()

print("Updated Battery")

print(

    battery.status()

)
history.save({

    "SOC": battery.soc,

    "Temperature": battery.temperature,

    "Grid_Load": grid["grid_load"],

    "Cloud_Cover": cloud_cover,

    "Decision": decision["action"],

    "Current": decision["current"]

})
print()

print("Simulation Completed Successfully")