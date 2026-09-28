import joblib
import pandas as pd


class BatteryInference:

    def __init__(self):

        self.model = joblib.load(
            "models/battery_model.pkl"
        )

    # ------------------------------------

    def predict(

        self,

        temperature,

        soc,

        battery_health,

        charging_current

    ):

        sample = pd.DataFrame(

            [[

                temperature,

                soc,

                battery_health,

                charging_current

            ]],

            columns=[

                "temperature",

                "soc",

                "battery_health",

                "charging_current"

            ]

        )

        prediction = self.model.predict(sample)

        return prediction[0]