class CoordinatorAgent:

    def decide(
        self,
        battery_decision,
        tariff_decision,
        solar_decision,
        grid_decision,
        user_decision,
        schedule=None
    ):

        # --------------------------------------------------
        # 1. BATTERY SAFETY
        # --------------------------------------------------

        if battery_decision["action"] == "STOP":

            return {
                "action": "STOP_CHARGING",
                "current": 0,
                "mode": "SAFETY_STOP",
                "reason":
                    "Battery safety limit reached"
            }

        # --------------------------------------------------
        # 2. GRID CRITICAL
        # --------------------------------------------------

        if grid_decision["action"] == "DELAY":

            return {
                "action": "WAIT",
                "current": 0,
                "mode": "GRID_WAIT",
                "reason":
                    "Grid overloaded"
            }

        # --------------------------------------------------
        # 3. DETERMINE DEADLINE PRESSURE
        # --------------------------------------------------

        pressure = "LOW"

        if schedule:

            pressure = schedule.get(
                "deadline_pressure",
                "LOW"
            )

        # --------------------------------------------------
        # 4. BASE CURRENT
        # --------------------------------------------------

        if pressure == "LOW":

            requested_current = 16.0
            mode = "SLOW_CHARGING"

        elif pressure == "MEDIUM":

            requested_current = 24.0
            mode = "NORMAL_CHARGING"

        elif pressure == "HIGH":

            requested_current = 32.0
            mode = "FAST_CHARGING"

        else:

            requested_current = 32.0
            mode = "FAST_CHARGING"

        # --------------------------------------------------
        # 5. GRID LIMIT
        # --------------------------------------------------

        if grid_decision["action"] == "REDUCE_CURRENT":

            requested_current = min(
                requested_current,
                16.0
            )

            mode = "GRID_LIMITED"

        # --------------------------------------------------
        # 6. BATTERY LIMIT
        # --------------------------------------------------

        if battery_decision["action"] == "REDUCE":

            requested_current = min(
                requested_current,
                16.0
            )

            mode = "BATTERY_PROTECTED"

        # --------------------------------------------------
        # 7. USER REQUIREMENT
        # --------------------------------------------------

        if user_decision["action"] == "READY":

            return {
                "action": "WAIT",
                "current": 0,
                "mode": "TARGET_REACHED",
                "reason":
                    "Target SOC already satisfied"
            }

        # --------------------------------------------------
        # 8. SOLAR OPTIMIZATION
        # --------------------------------------------------

        if (
            pressure == "LOW"
            and
            solar_decision.get(
                "action"
            ) == "WAIT_FOR_SOLAR"
        ):

            return {
                "action": "WAIT",
                "current": 0,
                "mode": "SOLAR_WAIT",
                "reason":
                    "Waiting for better solar conditions"
            }

        # --------------------------------------------------
        # 9. START CHARGING
        # --------------------------------------------------

        return {

            "action":
                "START_CHARGING",

            "current":
                requested_current,

            "mode":
                mode,

            "reason":
                f"Deadline pressure: {pressure}"
        }