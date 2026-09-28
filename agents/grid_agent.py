class GridAgent:

    def analyze(self, grid):
        load = grid.get("grid_load", 0)

        if load >= 90:
            return {
                "status": "CRITICAL",
                "action": "DELAY",
                "current": 0,
                "reason": f"Grid Overloaded ({load}% capacity)"
            }

        elif load >= 75:
            return {
                "status": "HIGH",
                "action": "REDUCE_CURRENT",
                "current": 16,
                "reason": f"High Grid Demand ({load}% capacity)"
            }

        else:
            return {
                "status": "NORMAL",
                "action": "ALLOW",
                "current": 32,
                "reason": f"Grid Stable ({load}% capacity)"
            }