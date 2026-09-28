import random
import pandas as pd

data = []

for i in range(5000):

    hour = random.randint(0,23)

    monthly_units = random.randint(50,600)

    # Slab
    if monthly_units <= 100:
        slab = 1
    elif monthly_units <= 200:
        slab = 2
    elif monthly_units <= 400:
        slab = 3
    else:
        slab = 4

    # Labels
    if 18 <= hour <= 21:
        label = "WAIT"

    elif 10 <= hour <= 16:
        label = "CHARGE"

    elif slab == 4:
        label = "WAIT"

    else:
        label = "CHARGE"

    data.append([
        hour,
        monthly_units,
        slab,
        label
    ])

df = pd.DataFrame(
    data,
    columns=[
        "hour",
        "monthly_units",
        "slab",
        "label"
    ]
)

df.to_csv(
    "datasets/tariff_dataset.csv",
    index=False
)

print(df.head())
print("Tariff Dataset Created")