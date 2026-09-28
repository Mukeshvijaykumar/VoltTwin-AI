from pathlib import Path

import joblib
import pandas as pd

from fastapi import FastAPI
from pydantic import BaseModel
from agents.battery_agent import BatteryAgent
from agents.grid_agent import GridAgent
from agents.solar_agent import SolarAgent
from agents.tariff_agent import TariffAgent
from agents.user_agent import UserAgent
from agents.coordinator_agent import CoordinatorAgent

from simulation.battery import Battery
# -------------------------------------------------

BASE = Path(__file__).resolve().parent.parent

app = FastAPI(
    title="EV Charging Prediction API",
    version="1.0"
)

# -------------------------------------------------

model = joblib.load(
    BASE / "models" / "catboost.pkl"
)

print("Model Loaded Successfully")
battery_agent = BatteryAgent()
grid_agent = GridAgent()
solar_agent = SolarAgent()
tariff_agent = TariffAgent()
user_agent = UserAgent()
coordinator = CoordinatorAgent()
# -------------------------------------------------

class EVInput(BaseModel):

    Installed_Capacity_MW: float
    Today_Program: float
    Today_Actual: float

    temperature: float
    humidity: float
    wind_speed: float
    cloud_cover: float

# -------------------------------------------------
class ChargingInput(BaseModel):

    current_soc: float
    required_soc: float

    temperature: float
    health: float
    charging_current: float

    grid_load: float

    cloud_cover: float

    current_units: float
    charging_units: float
    current_hour: int
@app.get("/")
def home():

    return {
        "message": "EV Charging AI API Running"
    }

# -------------------------------------------------

@app.post("/predict")
def predict(data: EVInput):

    df = pd.DataFrame([{

        "Installed_Capacity_MW":
            data.Installed_Capacity_MW,

        "Today_Program":
            data.Today_Program,

        "Today_Actual":
            data.Today_Actual,

        "temperature":
            data.temperature,

        "humidity":
            data.humidity,

        "wind_speed":
            data.wind_speed,

        "cloud_cover":
            data.cloud_cover

    }])

    prediction = model.predict(df)

    return {

        "Predicted_EV_Demand":

            round(float(prediction[0]),2)

    }
@app.post("/smart-charge")
def smart_charge(data: ChargingInput):

    # -----------------------------
    # Create Digital Twin Battery
    # -----------------------------

    battery = Battery(
        soc=data.current_soc,
        temperature=data.temperature,
        health=data.health,
        charging_current=data.charging_current
    )

    # -----------------------------
    # Battery Agent
    # -----------------------------

    battery_result = battery_agent.analyze(battery)

    # -----------------------------
    # Grid Agent
    # -----------------------------

    grid_result = grid_agent.analyze({
        "grid_load": data.grid_load
    })

    # -----------------------------
    # Solar Agent
    # -----------------------------

    solar_result = solar_agent.analyze(
        data.cloud_cover
    )

    # -----------------------------
    # Tariff Agent
    # -----------------------------

    tariff_result = tariff_agent.analyze(

        data.current_units,

        data.charging_units,

        data.current_hour

    )

    # -----------------------------
    # User Agent
    # -----------------------------

    user_result = user_agent.analyze(

        data.current_soc,

        data.required_soc

    )

    # -----------------------------
    # Coordinator
    # -----------------------------

    decision = coordinator.decide(

        battery_result,

        tariff_result,

        solar_result,

        grid_result,

        user_result

    )

    # -----------------------------
    # Return complete result
    # -----------------------------

    return {

        "battery_agent": battery_result,

        "grid_agent": grid_result,

        "solar_agent": solar_result,

        "tariff_agent": tariff_result,

        "user_agent": user_result,

        "final_decision": decision

    }