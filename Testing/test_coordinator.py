from agents.coordinator_agent import CoordinatorAgent

coordinator = CoordinatorAgent()

battery = {"action":"SAFE"}

tariff = {"tod_multiplier":1.2}

solar = {"action":"NORMAL"}

grid = {"action":"ALLOW"}

user = {"action":"WAIT"}

result = coordinator.decide(
    battery,
    tariff,
    solar,
    grid,
    user
)

print(result)