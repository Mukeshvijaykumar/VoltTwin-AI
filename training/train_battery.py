import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# -------------------------
# Load Dataset
# -------------------------

data = pd.read_csv("datasets/battery_dataset.csv")

# -------------------------
# Features (Input)
# -------------------------

X = data[
    [
        "temperature",
        "soc",
        "battery_health",
        "charging_current"
    ]
]

# -------------------------
# Target (Output)
# -------------------------

y = data["label"]

# -------------------------
# Split Dataset
# -------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# -------------------------
# Create Model
# -------------------------

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

# -------------------------
# Train Model
# -------------------------

model.fit(X_train, y_train)

# -------------------------
# Accuracy
# -------------------------

accuracy = model.score(X_test, y_test)

print()

print("Accuracy :", accuracy)

# -------------------------
# Save Model
# -------------------------

joblib.dump(
    model,
    "models/battery_model.pkl"
)

print()

print("Battery Model Saved Successfully")