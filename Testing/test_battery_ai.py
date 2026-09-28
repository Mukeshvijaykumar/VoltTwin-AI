from inference.battery_inference import BatteryInference


ai = BatteryInference()

result = ai.predict(

    temperature=46,

    soc=72,

    battery_health=92,

    charging_current=32

)

print()

print("Prediction")

print(result)