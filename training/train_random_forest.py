from pathlib import Path
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

# --------------------------------------------------
# Project Base Folder
# --------------------------------------------------

BASE = Path(__file__).resolve().parent.parent

# --------------------------------------------------
# Load Dataset
# --------------------------------------------------

file = BASE / "datasets" / "processed" / "training_dataset.csv"

df = pd.read_csv(file)

print("=" * 60)
print("Dataset Loaded Successfully")
print(df.head())

# --------------------------------------------------
# Select Features
# --------------------------------------------------

features = [
    "Installed_Capacity_MW",
    "Today_Program",
    "Today_Actual",
    "temperature",
    "humidity",
    "wind_speed",
    "cloud_cover"
]

target = "ev_demand"

X = df[features]

y = df[target]

print("\nFeature Shape :", X.shape)
print("Target Shape :", y.shape)

# --------------------------------------------------
# Train-Test Split
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)

print("\nTraining Samples :", len(X_train))
print("Testing Samples :", len(X_test))

# --------------------------------------------------
# Create Model
# --------------------------------------------------

model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)

# --------------------------------------------------
# Train
# --------------------------------------------------

print("\nTraining Model...")

model.fit(X_train, y_train)

print("Training Completed.")

# --------------------------------------------------
# Prediction
# --------------------------------------------------

predictions = model.predict(X_test)

# --------------------------------------------------
# Evaluation
# --------------------------------------------------

mae = mean_absolute_error(y_test, predictions)

mse = mean_squared_error(y_test, predictions)

rmse = mse ** 0.5

r2 = r2_score(y_test, predictions)

print("\nModel Performance")

print("MAE  :", round(mae, 2))
print("RMSE :", round(rmse, 2))
print("R²   :", round(r2, 4))

# --------------------------------------------------
# Save Model
# --------------------------------------------------

model_path = BASE / "models" / "random_forest.pkl"

joblib.dump(model, model_path)

print("\nModel Saved Successfully")

print(model_path)