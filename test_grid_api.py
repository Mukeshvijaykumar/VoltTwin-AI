from services.grid_service import GridService
from agents.grid_agent import GridAgent


if __name__ == "__main__":

    service = GridService(zone="IN-SO")

    agent = GridAgent()


    # ------------------------------------------------------------
    # GET GRID DATA
    # ------------------------------------------------------------

    grid_status = service.get_grid_status()


    # ------------------------------------------------------------
    # AI GRID DECISION
    # ------------------------------------------------------------

    decision = agent.analyze(
        grid_status
    )


    print("\n" + "=" * 60)
    print("GRID DATA PIPELINE")
    print("=" * 60)

    print(
        f"Zone           : {service.zone}"
    )

    print(
        f"Data Source    : {grid_status['source']}"
    )

    print(
        f"Demand         : {grid_status['demand_mw']} MW"
    )

    print(
        f"Grid Load      : {grid_status['grid_load']}%"
    )

    print(
        f"Timestamp      : {grid_status['timestamp']}"
    )

    print(
        f"Estimated      : {grid_status['is_estimated']}"
    )

    print(
        f"Live Data      : {grid_status['is_live']}"
    )


    print("\n" + "=" * 60)
    print("GRID AGENT DECISION")
    print("=" * 60)

    print(
        f"Status         : {decision['status']}"
    )

    print(
        f"Action         : {decision['action']}"
    )

    print(
        f"Current Limit  : {decision['current']} A"
    )

    print(
        f"Reason         : {decision['reason']}"
    )

    print("=" * 60)