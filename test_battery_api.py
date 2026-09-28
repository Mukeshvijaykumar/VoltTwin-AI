from services.battery_service import BatteryService


if __name__ == "__main__":

    battery_service = BatteryService()

    print("=" * 60)
    print("AUTOMATIC BATTERY TELEMETRY")
    print("=" * 60)

    for step in range(5):

        data = battery_service.get_battery_status()

        print("\nBattery Telemetry:")
        print(data)

        battery_service.simulate_charging(16)

    print("\n" + "=" * 60)
    print("BATTERY TELEMETRY TEST COMPLETED")
    print("=" * 60)