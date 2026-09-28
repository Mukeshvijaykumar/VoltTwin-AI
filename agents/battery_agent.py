from inference.battery_inference import BatteryInference


class BatteryAgent:

    def __init__(self):

        self.ai = BatteryInference()

    # ---------------------------------

    def analyze(self, battery):

        prediction = self.ai.predict(

            battery.temperature,

            battery.soc,

            battery.health,

            battery.charging_current

        )

        if prediction == "SAFE":

            return {

                "action": "ALLOW",

                "current": 32

            }

        elif prediction == "REDUCE":

            return {

                "action": "REDUCE",

                "current": 16

            }

        else:

            return {

                "action": "STOP",

                "current": 0

            }