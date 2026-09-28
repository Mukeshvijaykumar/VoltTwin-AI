from services.grid_service import GridService
from services.local_grid_service import LocalGridService


class GridManager:

    def __init__(self):

        self.live_grid = GridService(
            zone="IN-SO"
        )

        self.local_grid = LocalGridService()

    def get_grid_status(
        self,
        latitude,
        longitude,
        locality,
        district
    ):

        # --------------------------------
        # TRY LIVE GRID
        # --------------------------------

        try:

            live = (
                self.live_grid
                .get_grid_status()
            )

            if live.get(
                "is_live",
                False
            ):

                live["location"] = locality

                return live

        except Exception:
            pass

        # --------------------------------
        # LOCATION-AWARE FALLBACK
        # --------------------------------

        return (
            self.local_grid
            .get_grid_status(
                latitude,
                longitude,
                locality,
                district
            )
        )