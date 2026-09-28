class Charger:

    def __init__(self, battery):
        self.battery = battery
        self.current = 0
        self.status = "Idle"

    def start(self, current):
        self.current = current
        self.status = "Charging"

        self.battery.is_charging = True

    def stop(self):
        self.current = 0
        self.status = "Stopped"

        self.battery.is_charging = False