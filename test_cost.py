
from services.charging_cost_service import ChargingCostService


cost_service = ChargingCostService()

result = cost_service.calculate_step_cost(
    current=16,
    duration_minutes=10
)

print("Energy:", result["energy_kwh"], "kWh")
print("Cost: ₹", result["cost"])

print("\nTotal:")
print(cost_service.get_total_cost())