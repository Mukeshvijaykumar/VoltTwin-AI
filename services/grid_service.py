import os
import requests
from datetime import datetime


class GridService:

    def __init__(self, zone="IN-SO"):

        self.zone = zone
        self.api_key = os.getenv("ELECTRICITY_MAPS_API_KEY")

        self.base_url = "https://api.electricitymaps.com/v4"


    # ============================================================
    # GET GRID STATUS
    # ============================================================

    def get_grid_status(self):

        # --------------------------------------------------------
        # Check API key
        # --------------------------------------------------------

        if not self.api_key:

            print("[GridService] API key not configured.")

            return self._fallback_data()


        # --------------------------------------------------------
        # Electricity Maps API
        # --------------------------------------------------------

        url = f"{self.base_url}/total-reported-load/latest"

        params = {
            "zone": self.zone
        }

        headers = {
            "auth-token": self.api_key
        }


        try:

            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=10
            )


            # ----------------------------------------------------
            # Authentication problem
            # ----------------------------------------------------

            if response.status_code == 401:

                print(
                    "[GridService] API authentication failed."
                )

                return self._fallback_data()


            # ----------------------------------------------------
            # Invalid zone / request
            # ----------------------------------------------------

            if response.status_code == 400:

                print(
                    f"[GridService] Invalid API request for zone: "
                    f"{self.zone}"
                )

                return self._fallback_data()


            response.raise_for_status()


            data = response.json()

            return self._parse_live_data(data)


        except requests.RequestException as error:

            print(
                f"[GridService] Live grid request failed: {error}"
            )

            return self._fallback_data()


    # ============================================================
    # PARSE LIVE DATA
    # ============================================================

    def _parse_live_data(self, data):

        load_mw = data.get("value")

        timestamp = data.get("datetime")

        estimated = data.get(
            "isEstimated",
            False
        )


        if load_mw is None:

            print(
                "[GridService] Live response did not contain "
                "grid load."
            )

            return self._fallback_data()


        # --------------------------------------------------------
        # Reference capacity
        # --------------------------------------------------------

        reference_load_mw = 75000


        grid_load = (
            float(load_mw)
            / reference_load_mw
        ) * 100


        grid_load = max(
            0.0,
            min(
                100.0,
                round(grid_load, 2)
            )
        )


        return {

            "grid_load": grid_load,

            "demand_mw": round(
                float(load_mw),
                2
            ),

            "timestamp": timestamp,

            "source": (
                f"Electricity Maps Live ({self.zone})"
            ),

            "is_estimated": bool(estimated),

            "is_live": not bool(estimated),

            "is_peak": grid_load >= 70.0

        }


    # ============================================================
    # FALLBACK DATA
    # ============================================================

    def _fallback_data(self):

        return {

            "grid_load": 65.0,

            "demand_mw": None,

            "timestamp": datetime.now().isoformat(),

            "source": "CEA Benchmark (Fallback)",

            "is_estimated": True,

            "is_live": False,

            "is_peak": False

        }