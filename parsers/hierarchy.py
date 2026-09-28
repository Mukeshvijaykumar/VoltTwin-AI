class Hierarchy:

    def __init__(self):

        self.region = ""
        self.state = ""
        self.sector = ""
        self.type = ""

    def set_region(self, value):
        self.region = value

    def set_state(self, value):
        self.state = value

    def set_sector(self, value):
        self.sector = value

    def set_type(self, value):
        self.type = value

    def get(self):
        return {
            "Region": self.region,
            "State": self.state,
            "Sector": self.sector,
            "Type": self.type
        }