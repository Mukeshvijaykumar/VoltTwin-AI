import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

data = pd.read_csv("datasets/tariff_dataset.csv")

X = data[
    [
        "hour",
        "monthly_units",
        "slab"
    ]
]

y = data["label"]

# Convert labels to numbers
mapping = {
    "CHARGE":0,
    "WAIT":1
}

y = y.map(mapping)

X_train,X_test,y_train,y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

model = XGBClassifier()

model.fit(
    X_train,
    y_train
)

print()

print(
    "Accuracy:",
    model.score(
        X_test,
        y_test
    )
)

joblib.dump(
    model,
    "models/tariff_model.pkl"
)

print("Tariff Model Saved")