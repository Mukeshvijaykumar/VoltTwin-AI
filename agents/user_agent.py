class UserAgent:

    def analyze(self,
                current_soc,
                required_soc):

        if current_soc >= required_soc:

            return {

                "status": "READY",
                "action": "WAIT",
                "reason": "Battery already sufficient"

            }

        return {

            "status": "NEED_CHARGE",
            "action": "START",
            "reason": "Battery needs charging"

        }