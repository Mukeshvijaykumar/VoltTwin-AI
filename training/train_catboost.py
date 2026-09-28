from pathlib import Path
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

from catboost import CatBoostRegressor

# --------------------------------------------
# Base Path
# --------------------------------------------

BASE = Path(__file__).resolve().parent.parent

# --------------------------------------------
# Load Dataset
# --------------------------------------------

df = pd.read_csv(
    BASE / "datasets" / "processed" / "training_dataset.csv"
)

print("=" * 60)
print("Dataset Loaded Successfully")
print(df.head())

# --------------------------------------------
# Features
# --------------------------------------------

features = [
    "Installed_Capacity_MW",
    "Today_Program",
    "Today_Actual",
    "temperature",
    "humidity",
    "wind_speed",
    "cloud_cover"
]

X = df[features]
y = df["ev_demand"]

print("\nFeature Shape :", X.shape)
print("Target Shape :", y.shape)

# --------------------------------------------
# Train Test Split
# --------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)

print("\nTraining Samples :", len(X_train))
print("Testing Samples :", len(X_test))

# --------------------------------------------
# Model
# --------------------------------------------

model = CatBoostRegressor(
    iterations=300,
    learning_rate=0.05,
    depth=6,
    random_seed=42,
    verbose=False
)

print("\nTraining CatBoost Model...")

model.fit(X_train, y_train)

print("Training Completed.")

# --------------------------------------------
# Prediction
# --------------------------------------------

predictions = model.predict(X_test)

mae = mean_absolute_error(y_test, predictions)
rmse = mean_squared_error(y_test, predictions) ** 0.5
r2 = r2_score(y_test, predictions)

print("\nModel Performance")
print("MAE  :", round(mae, 2))
print("RMSE :", round(rmse, 2))
print("R²   :", round(r2, 4))

# --------------------------------------------
# Save Model
# --------------------------------------------

models = BASE / "models"
models.mkdir(exist_ok=True)

joblib.dump(
    model,
    models / "catboost.pkl"
)

print("\nModel Saved Successfully")
print(models / "catboost.pkl")