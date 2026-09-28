import os

folders = [

    "datasets/raw/weather",

    "datasets/raw/grid",

    "datasets/raw/renewable",

    "datasets/raw/tariff",

    "datasets/raw/holidays",

    "datasets/raw/charging_logs",

    "datasets/processed",

    "datasets/final"

]

for folder in folders:

    os.makedirs(folder, exist_ok=True)

print("Research folders verified successfully.")