from pathlib import Path
import joblib
import pandas as pd

# -------------------------------------
# Base Path
# -------------------------------------

BASE = Path(__file__).resolve().parent.parent

# -------------------------------------
# Load Model
# -------------------------------------

model = joblib.load(
    BASE / "models" / "catboost.pkl"
)

print("CatBoost Model Loaded Successfully")

# -------------------------------------
# Sample Input
# -------------------------------------

sample = pd.DataFrame({
    "Installed_Capacity_MW": [1200],
    "Today_Program": [2500],
    "Today_Actual": [2400],
    "temperature": [34],
    "humidity": [65],
    "wind_speed": [8],
    "cloud_cover": [55]
})

print("\nInput Data")
print(sample)

# -------------------------------------
# Prediction
# -------------------------------------

prediction = model.predict(sample)

print("\nPredicted EV Demand")
print(round(prediction[0], 2))