class Battery:

    def __init__(
        self,
        capacity=40,
        soc=50,
        temperature=30,
        health=100
    ):
        self.capacity = capacity
        self.soc = soc
        self.temperature = temperature
        self.health = health
        self.is_charging = False

    def start_charging(self):
        self.is_charging = True

    def stop_charging(self):
        self.is_charging = False

    def update_soc(self, value):
        self.soc = value

    def update_temperature(self, temp):
        self.temperature = temp