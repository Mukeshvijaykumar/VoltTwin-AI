class VirtualCharger:

    def __init__(self):

        self.status = "IDLE"
        self.current = 0.0
        self.voltage = 230.0
        self.power_kw = 0.0
        self.mode = "IDLE"

    def execute(self, decision):

        action = decision.get(
            "action",
            "WAIT"
        )

        current = float(
            decision.get(
                "current",
                0
            )
        )

        mode = decision.get(
            "mode",
            "IDLE"
        )

        if action == "START_CHARGING":

            self.status = "CHARGING"
            self.current = current
            self.mode = mode

        elif action == "STOP_CHARGING":

            self.status = "STOPPED"
            self.current = 0.0
            self.mode = mode

        elif action == "WAIT":

            self.status = "WAITING"
            self.current = 0.0
            self.mode = mode

        else:

            self.status = "IDLE"
            self.current = 0.0
            self.mode = "IDLE"

        self.power_kw = (
            self.voltage *
            self.current /
            1000.0
        )

        return self.get_status()

    def get_status(self):

        return {

            "status": self.status,

            "current": round(
                self.current,
                2
            ),

            "voltage": round(
                self.voltage,
                2
            ),

            "power_kw": round(
                self.power_kw,
                3
            ),

            "mode": self.mode
        }