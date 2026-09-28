import random
import pandas as pd

data = []

for i in range(5000):

    temperature = random.randint(25,55)

    soc = random.randint(10,100)

    battery_health = random.randint(80,100)

    charging_current = random.choice([10,16,20,25,32])

    # Label Creation
    if temperature >= 48:
        label = "STOP"

    elif temperature >= 42:
        label = "REDUCE"

    else:
        label = "SAFE"

    data.append([
        temperature,
        soc,
        battery_health,
        charging_current,
        label
    ])

columns = [
    "temperature",
    "soc",
    "battery_health",
    "charging_current",
    "label"
]

df = pd.DataFrame(data, columns=columns)

df.to_csv(
    "datasets/battery_dataset.csv",
    index=False
)

print(df.head())

print()

print("Dataset Created Successfully")