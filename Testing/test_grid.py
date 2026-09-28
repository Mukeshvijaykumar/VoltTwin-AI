from services.grid_service import GridService
from agents.grid_agent import GridAgent


service = GridService()

agent = GridAgent()

grid = service.get_grid_status()

print("\nGrid Status")

print(grid)

decision = agent.analyze(grid)

print("\nGrid Agent Decision")

print(decision)