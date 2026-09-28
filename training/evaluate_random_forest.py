from pathlib import Path
import joblib
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split

# --------------------------------------------------
# Base Folder
# --------------------------------------------------

BASE = Path(__file__).resolve().parent.parent

# --------------------------------------------------
# Load Dataset
# --------------------------------------------------

df = pd.read_csv(
    BASE / "datasets" / "processed" / "training_dataset.csv"
)

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

# --------------------------------------------------
# Same Train/Test Split
# --------------------------------------------------

_, X_test, _, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)

# --------------------------------------------------
# Load Saved Model
# --------------------------------------------------

model = joblib.load(
    BASE / "models" / "random_forest.pkl"
)

predictions = model.predict(X_test)

# --------------------------------------------------
# Plot
# --------------------------------------------------

plt.figure(figsize=(10, 6))

plt.scatter(
    y_test,
    predictions,
    alpha=0.7
)

plt.plot(
    [y_test.min(), y_test.max()],
    [y_test.min(), y_test.max()],
    'r--',
    linewidth=2
)

plt.xlabel("Actual EV Demand")
plt.ylabel("Predicted EV Demand")
plt.title("Random Forest Predictions")

plt.grid(True)

plt.show()