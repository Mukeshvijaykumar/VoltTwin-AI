class SolarAgent:

    def analyze(self, cloud_cover):

        if cloud_cover < 30:

            return {

                "status": "HIGH_SOLAR",
                "action": "WAIT_FOR_SOLAR",
                "reason": "Excellent solar generation"

            }

        elif cloud_cover < 70:

            return {

                "status": "MEDIUM_SOLAR",
                "action": "ALLOW",
                "reason": "Moderate solar generation"

            }

        else:

            return {

                "status": "LOW_SOLAR",
                "action": "ALLOW",
                "reason": "Very little solar generation"

            }