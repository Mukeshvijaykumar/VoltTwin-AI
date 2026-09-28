import os
import sys
from datetime import datetime, date, timedelta, time as dt_time
from zoneinfo import ZoneInfo

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from streamlit_geolocation import streamlit_geolocation

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from services.location_service import LocationService
from services.charging_scheduler import ChargingScheduler
from simulation.charging_controller import ChargingController

IST = ZoneInfo("Asia/Kolkata")

st.set_page_config(
    page_title="AI Smart EV Charging",
    page_icon="🔋",
    layout="wide"
)

st.markdown(
    """
    <style>
    .main .block-container {
        max-width: 1450px;
        padding-top: 1.2rem;
        padding-bottom: 2.5rem;
    }

    .hero {
        padding: 1rem 1.25rem;
        border: 1px solid #e6e9ef;
        border-radius: 15px;
        background: linear-gradient(135deg, #f8fbff, #ffffff);
        margin-bottom: 1rem;
    }

    .hero h1 {
        margin: 0;
        font-size: 2rem;
        line-height: 1.2;
    }

    .hero p {
        margin: .35rem 0 0;
        color: #64748b;
        font-size: .95rem;
    }

    .section-title {
        font-size: 1.15rem;
        font-weight: 700;
        margin: 1rem 0 .65rem;
    }

    .card {
        border: 1px solid #e6e9ef;
        border-radius: 13px;
        padding: .9rem 1rem;
        background: white;
        min-height: 105px;
        box-shadow: 0 2px 8px rgba(15, 23, 42, .035);
    }

    .card-label {
        font-size: .80rem;
        color: #64748b;
        margin-bottom: .30rem;
    }

    .card-value {
        font-size: 1.20rem;
        font-weight: 700;
        line-height: 1.2;
        word-break: break-word;
    }

    .card-sub {
        font-size: .76rem;
        color: #64748b;
        margin-top: .3rem;
    }

    .small-note {
        font-size: .8rem;
        color: #64748b;
    }
    </style>
    """,
    unsafe_allow_html=True
)


def value(record, key, default=None):
    item = record.get(key, default)
    return default if item is None else item


def metric_card(label, display_value, sub=""):
    return f"""
    <div class="card">
        <div class="card-label">{label}</div>
        <div class="card-value">{display_value}</div>
        <div class="card-sub">{sub}</div>
    </div>
    """


def money(amount):
    try:
        return f"₹{float(amount):.2f}"
    except (TypeError, ValueError):
        return "₹0.00"


def hours_text(minutes):
    if minutes is None:
        return "N/A"

    try:
        return f"{float(minutes) / 60:.2f} h"
    except (TypeError, ValueError):
        return "N/A"


def safe_float(value_, default=0.0):
    try:
        return float(value_)
    except (TypeError, ValueError):
        return default


def make_soc_temperature_chart(df):
    fig = go.Figure()

    if not df.empty:
        fig.add_trace(
            go.Scatter(
                x=df["simulation_hours"],
                y=df["soc"],
                mode="lines+markers",
                name="SOC (%)"
            )
        )

        fig.add_trace(
            go.Scatter(
                x=df["simulation_hours"],
                y=df["temperature"],
                mode="lines+markers",
                name="Temperature (°C)",
                yaxis="y2"
            )
        )

    fig.update_layout(
        height=330,
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis=dict(
            title="Simulation Time (hours)",
            rangemode="tozero"
        ),
        yaxis=dict(
            title="SOC (%)",
            range=[0, 100],
            fixedrange=True
        ),
        yaxis2=dict(
            title="Temperature (°C)",
            overlaying="y",
            side="right",
            range=[25, 50],
            fixedrange=True
        ),
        legend=dict(
            orientation="h",
            y=1.08,
            x=0
        ),
        hovermode="x unified"
    )

    return fig


def make_current_grid_chart(df):
    fig = go.Figure()

    if not df.empty:
        fig.add_trace(
            go.Scatter(
                x=df["simulation_hours"],
                y=df["current"],
                mode="lines+markers",
                name="Charging Current (A)"
            )
        )

        fig.add_trace(
            go.Scatter(
                x=df["simulation_hours"],
                y=df["grid_load"],
                mode="lines+markers",
                name="Grid Load (%)",
                yaxis="y2"
            )
        )

    fig.update_layout(
        height=330,
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis=dict(
            title="Simulation Time (hours)",
            rangemode="tozero"
        ),
        yaxis=dict(
            title="Charging Current (A)",
            range=[0, 34],
            fixedrange=True
        ),
        yaxis2=dict(
            title="Grid Load (%)",
            overlaying="y",
            side="right",
            range=[0, 100],
            fixedrange=True
        ),
        legend=dict(
            orientation="h",
            y=1.08,
            x=0
        ),
        hovermode="x unified"
    )

    return fig


if "running" not in st.session_state:
    st.session_state.running = False

if "finished" not in st.session_state:
    st.session_state.finished = False

if "controller" not in st.session_state:
    st.session_state.controller = None

if "records" not in st.session_state:
    st.session_state.records = []

if "plug_in_time" not in st.session_state:
    st.session_state.plug_in_time = None


st.markdown(
    """
    <div class="hero">
        <h1>🔋 AI Smart EV Charging Control Center</h1>
        <p>
            Multi-Agent AI • Digital Twin • Virtual Smart Charger
            • Deadline-Aware Charging
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


with st.sidebar:
    st.header("⚙️ Charging Configuration")

    st.caption(
        "Battery SOC, temperature and health are managed "
        "automatically by the Digital Twin."
    )

    target_soc = st.slider(
        "Target SOC (%)",
        min_value=50,
        max_value=100,
        value=90
    )

    st.divider()

    st.subheader("🕐 Departure Requirement")

    now_ist = datetime.now(IST)

    departure_date = st.date_input(
        "Departure Date",
        value=now_ist.date() + timedelta(days=1)
    )

    departure_time = st.time_input(
        "Departure Time",
        value=dt_time(18, 0)
    )

    departure_datetime = datetime.combine(
        departure_date,
        departure_time
    ).replace(tzinfo=IST)

    if (
        departure_date == now_ist.date()
        and departure_datetime <= now_ist
    ):
        departure_datetime += timedelta(days=1)

    st.caption(
        "All scheduling uses Asia/Kolkata (IST)."
    )

    st.divider()

    st.subheader("📍 Vehicle Location")

    location_data = streamlit_geolocation()

    if (
        location_data
        and location_data.get("latitude") is not None
        and location_data.get("longitude") is not None
    ):
        latitude = safe_float(
            location_data.get("latitude")
        )
        longitude = safe_float(
            location_data.get("longitude")
        )

        accuracy = location_data.get(
            "accuracy"
        )

        st.success("GPS Location Detected")

        st.caption(
            f"Latitude: {latitude:.6f}"
        )

        st.caption(
            f"Longitude: {longitude:.6f}"
        )

        if accuracy is not None:
            st.caption(
                f"Reported GPS accuracy: "
                f"±{safe_float(accuracy):.0f} m"
            )
    else:
        latitude = None
        longitude = None

        st.info(
            "Allow browser location access "
            "before starting."
        )

    st.divider()

    st.caption(
        "Simulation: 1 simulated minute per control cycle"
    )

    if st.button(
        "↺ Reset Session",
        use_container_width=True
    ):
        for key in [
            "running",
            "finished",
            "controller",
            "records",
            "plug_in_time"
        ]:
            st.session_state.pop(
                key,
                None
            )

        st.rerun()


location = None

if (
    latitude is not None
    and longitude is not None
):
    try:
        location = LocationService().reverse_geocode(
            latitude,
            longitude
        )
    except Exception:
        location = {
            "locality": "Current Location",
            "district": "",
            "state": "",
            "country": "India",
            "display_name": "Current Location"
        }


st.markdown(
    '<div class="section-title">🚀 Charging Control</div>',
    unsafe_allow_html=True
)

if latitude is None:
    st.warning(
        "Allow browser location access before "
        "starting the charging simulation."
    )

    start = st.button(
        "🚀 START INTELLIGENT CHARGING",
        use_container_width=True,
        disabled=True
    )
else:
    start = st.button(
        "🚀 START INTELLIGENT CHARGING",
        use_container_width=True,
        type="primary"
    )


if start:
    controller = ChargingController(
        target_soc=target_soc,
        departure_time=departure_datetime
    )

    st.session_state.controller = controller
    st.session_state.records = []
    st.session_state.plug_in_time = datetime.now(IST)
    st.session_state.running = True
    st.session_state.finished = False

    st.rerun()


if (
    not st.session_state.running
    and not st.session_state.finished
):
    scheduler = ChargingScheduler(
        battery_capacity_kwh=40.0,
        charger_power_kw=7.36
    )

    preview = scheduler.create_schedule(
        current_soc=42.0,
        target_soc=target_soc,
        departure_time=departure_datetime,
        current_time=datetime.now(IST)
    )

    st.markdown(
        '<div class="section-title">'
        '🕐 Charging Schedule Preview'
        '</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Current SOC",
        "42.0%"
    )

    col2.metric(
        "Required Energy",
        f'{preview["required_energy_kwh"]:.2f} kWh'
    )

    col3.metric(
        "Estimated Charge",
        hours_text(
            preview["estimated_charging_minutes"]
        )
    )

    col4.metric(
        "Available Time",
        hours_text(
            preview["available_minutes"]
        )
    )

    if preview["status"] == "INSUFFICIENT_TIME":
        st.warning(
            "⚠️ The selected departure time does not "
            "provide enough estimated time to reach "
            "the target at the nominal charging rate."
        )
    else:
        st.success(
            f'Schedule: {preview["status"]} • '
            f'Pressure: {preview["deadline_pressure"]}'
        )


if st.session_state.controller is not None:

    run_every = (
        0.5
        if st.session_state.running
        else None
    )

    @st.fragment(run_every=run_every)
    def live_dashboard():

        controller = st.session_state.controller
        records = st.session_state.records

        if st.session_state.running:
            record = controller.run_cycle(
                latitude,
                longitude
            )

            records.append(record)
            st.session_state.records = records

            if record.get("state") in [
                "COMPLETED",
                "DEADLINE_MISSED"
            ]:
                st.session_state.running = False
                st.session_state.finished = True

        if not records:
            return

        record = records[-1]
        df = pd.DataFrame(records)

        df["simulation_hours"] = (
            pd.to_numeric(
                df["simulation_minutes"],
                errors="coerce"
            ).fillna(0) / 60.0
        )

        state = value(
            record,
            "state",
            "RUNNING"
        )

        if state == "COMPLETED":
            st.success(
                f'✅ Charging completed — target SOC '
                f'reached at '
                f'{safe_float(value(record, "soc")):.1f}%.'
            )
        elif state == "DEADLINE_MISSED":
            st.error(
                "⛔ Departure deadline reached before "
                "target SOC was achieved."
            )
        elif state == "COOLING":
            st.warning(
                "❄️ Battery cooling active — charging "
                "temporarily paused."
            )
        elif state == "WAITING_GRID":
            st.warning(
                "⚡ Grid constraint — charging is waiting."
            )
        else:
            st.info(
                "🟢 System active — "
                + state.replace("_", " ").title()
            )

        st.markdown(
            '<div class="section-title">'
            '🔋 Digital Twin Battery'
            '</div>',
            unsafe_allow_html=True
        )

        cols = st.columns(5)

        cols[0].markdown(
            metric_card(
                "SOC",
                f'{safe_float(value(record, "soc")):.1f}%',
                f'Target {target_soc}%'
            ),
            unsafe_allow_html=True
        )

        cols[1].markdown(
            metric_card(
                "Temperature",
                f'{safe_float(value(record, "temperature")):.1f} °C',
                "Battery temperature"
            ),
            unsafe_allow_html=True
        )

        cols[2].markdown(
            metric_card(
                "Health",
                f'{safe_float(value(record, "health")):.1f}%',
                "Battery health"
            ),
            unsafe_allow_html=True
        )

        cols[3].markdown(
            metric_card(
                "Current",
                f'{safe_float(value(record, "current")):.1f} A',
                "AI charging current"
            ),
            unsafe_allow_html=True
        )

        cols[4].markdown(
            metric_card(
                "Power",
                f'{safe_float(value(record, "power_kw")):.2f} kW',
                "Virtual charger"
            ),
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-title">'
            '🌐 Live Operating Conditions'
            '</div>',
            unsafe_allow_html=True
        )

        cols = st.columns(4)

        cols[0].markdown(
            metric_card(
                "Weather",
                f'{safe_float(value(record, "weather_temperature")):.1f} °C',
                "Open-Meteo"
            ),
            unsafe_allow_html=True
        )

        cols[1].markdown(
            metric_card(
                "Humidity",
                f'{safe_float(value(record, "humidity")):.0f}%',
                "Relative humidity"
            ),
            unsafe_allow_html=True
        )

        cols[2].markdown(
            metric_card(
                "Cloud Cover",
                f'{safe_float(value(record, "cloud_cover")):.0f}%',
                "Solar condition"
            ),
            unsafe_allow_html=True
        )

        cols[3].markdown(
            metric_card(
                "Wind",
                f'{safe_float(value(record, "wind_speed")):.1f} km/h',
                "Wind speed"
            ),
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-title">'
            '⚡ Grid &nbsp;&nbsp; ☀️ Solar'
            '</div>',
            unsafe_allow_html=True
        )

        cols = st.columns(4)

        grid_load = safe_float(
            value(record, "grid_load")
        )

        cloud = safe_float(
            value(record, "cloud_cover"),
            100
        )

        if cloud < 30:
            solar_text = "HIGH"
        elif cloud < 70:
            solar_text = "MEDIUM"
        else:
            solar_text = "LOW"

        cols[0].markdown(
            metric_card(
                "Grid Load",
                f"{grid_load:.1f}%",
                value(
                    record,
                    "grid_status",
                    "NORMAL"
                )
            ),
            unsafe_allow_html=True
        )

        cols[1].markdown(
            metric_card(
                "Grid Source",
                (
                    "LIVE"
                    if value(
                        record,
                        "grid_is_live",
                        False
                    )
                    else "ESTIMATED"
                ),
                value(
                    record,
                    "grid_source",
                    "Simulation"
                )
            ),
            unsafe_allow_html=True
        )

        cols[2].markdown(
            metric_card(
                "Solar Availability",
                solar_text,
                f"Cloud cover {cloud:.0f}%"
            ),
            unsafe_allow_html=True
        )

        cols[3].markdown(
            metric_card(
                "Grid Demand",
                f'{safe_float(value(record, "grid_demand_mw")):.2f} MW',
                "Estimated / reported"
            ),
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-title">'
            '🧠 AI Coordinator Decision'
            '</div>',
            unsafe_allow_html=True
        )

        decision = value(
            record,
            "coordinator",
            {}
        )

        if not isinstance(decision, dict):
            decision = {}

        cols = st.columns(4)

        cols[0].markdown(
            metric_card(
                "AI Action",
                decision.get(
                    "action",
                    value(record, "action", "WAIT")
                ),
                "Coordinator decision"
            ),
            unsafe_allow_html=True
        )

        cols[1].markdown(
            metric_card(
                "Recommended Current",
                f'{safe_float(decision.get("current", 0)):.1f} A',
                "Requested current"
            ),
            unsafe_allow_html=True
        )

        cols[2].markdown(
            metric_card(
                "Charging Mode",
                decision.get(
                    "mode",
                    value(record, "mode", "IDLE")
                ),
                "Control mode"
            ),
            unsafe_allow_html=True
        )

        cols[3].markdown(
            metric_card(
                "Decision Reason",
                decision.get(
                    "reason",
                    value(record, "reason", "")
                ),
                "Why this decision was made"
            ),
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-title">'
            '🕐 Deadline-Aware Scheduler'
            '</div>',
            unsafe_allow_html=True
        )

        cols = st.columns(5)

        cols[0].metric(
            "Deadline Pressure",
            value(
                record,
                "deadline_pressure",
                "N/A"
            )
        )

        cols[1].metric(
            "Required Energy",
            f'{safe_float(value(record, "required_energy_kwh")):.2f} kWh'
        )

        cols[2].metric(
            "Available Time",
            hours_text(
                value(
                    record,
                    "available_minutes"
                )
            )
        )

        cols[3].metric(
            "Estimated Charge",
            hours_text(
                value(
                    record,
                    "estimated_charging_minutes"
                )
            )
        )

        controller_departure = getattr(
            controller,
            "departure_time",
            None
        )

        cols[4].metric(
            "Departure",
            (
                controller_departure.strftime(
                    "%d-%m-%Y %I:%M %p"
                )
                if controller_departure
                else "N/A"
            )
        )

        st.markdown(
            '<div class="section-title">'
            '⏱️ Automatic Simulation Clock'
            '</div>',
            unsafe_allow_html=True
        )

        simulation_time = getattr(
            controller,
            "simulation_time",
            None
        )

        simulation_minutes = getattr(
            controller,
            "total_simulation_minutes",
            0
        )

        simulation_time_text = (
            simulation_time.strftime(
                "%d-%m-%Y %I:%M:%S %p"
            )
            if simulation_time
            else "N/A"
        )

        cols = st.columns(4)

        cols[0].markdown(
            metric_card(
                "Simulation Elapsed",
                f"{safe_float(simulation_minutes) / 60:.2f} h",
                "Simulated time"
            ),
            unsafe_allow_html=True
        )

        cols[1].markdown(
            metric_card(
                "Simulation Time",
                simulation_time_text,
                "IST Digital Twin clock"
            ),
            unsafe_allow_html=True
        )

        plug_in_time = st.session_state.plug_in_time

        cols[2].markdown(
            metric_card(
                "Plug-in Time",
                (
                    plug_in_time.strftime(
                        "%I:%M:%S %p"
                    )
                    if plug_in_time
                    else "N/A"
                ),
                "Real session time"
            ),
            unsafe_allow_html=True
        )

        cols[3].markdown(
            metric_card(
                "Departure",
                (
                    controller_departure.strftime(
                        "%I:%M %p"
                    )
                    if controller_departure
                    else "N/A"
                ),
                "Deadline"
            ),
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-title">'
            '🔌 Virtual Smart Charger'
            '</div>',
            unsafe_allow_html=True
        )

        charger = value(
            record,
            "charger_status",
            {}
        )

        if not isinstance(charger, dict):
            charger = {}

        cols = st.columns(4)

        cols[0].metric(
            "Status",
            charger.get(
                "status",
                "UNKNOWN"
            )
        )

        cols[1].metric(
            "Current",
            f'{safe_float(charger.get("current")):.1f} A'
        )

        cols[2].metric(
            "Voltage",
            f'{safe_float(charger.get("voltage"), 230):.0f} V'
        )

        cols[3].metric(
            "Power",
            f'{safe_float(charger.get("power_kw")):.2f} kW'
        )

        st.markdown(
            '<div class="section-title">'
            '🌡️ Thermal Protection &nbsp;&nbsp; 💰 Charging Cost'
            '</div>',
            unsafe_allow_html=True
        )

        cols = st.columns(6)

        cols[0].metric(
            "Cooling",
            "ACTIVE"
            if value(record, "cooling", False)
            else "NORMAL"
        )

        cols[1].metric(
            "Cooling Cycles",
            int(
                safe_float(
                    value(record, "cooling_cycles")
                )
            )
        )

        cols[2].metric(
            "Auto Restarts",
            int(
                safe_float(
                    value(record, "restart_count")
                )
            )
        )

        cols[3].metric(
            "Energy This Cycle",
            f'{safe_float(value(record, "energy_kwh")):.3f} kWh'
        )

        cols[4].metric(
            "Cycle Cost",
            money(
                value(
                    record,
                    "step_cost",
                    0
                )
            )
        )

        cols[5].metric(
            "Total Cost",
            money(
                value(
                    record,
                    "total_cost",
                    0
                )
            )
        )

        st.caption(
            f'Tariff: ₹{safe_float(value(record, "tariff_rate")):.2f}/kWh • '
            f'Period: {value(record, "tariff_period", "N/A")} • '
            f'Slab rate: ₹{safe_float(value(record, "tariff_slab_rate")):.2f}'
        )

        st.markdown(
            '<div class="section-title">'
            '🤖 Multi-Agent Decision Layer'
            '</div>',
            unsafe_allow_html=True
        )

        agent_columns = st.columns(5)

        agents = [
            (
                "Battery",
                value(record, "battery_agent", {})
            ),
            (
                "Grid",
                value(record, "grid_agent", {})
            ),
            (
                "Solar",
                value(record, "solar_agent", {})
            ),
            (
                "Tariff",
                value(record, "tariff_agent", {})
            ),
            (
                "User",
                value(record, "user_agent", {})
            )
        ]

        for column, (name, data) in zip(
            agent_columns,
            agents
        ):
            if not isinstance(data, dict):
                data = {}

            agent_status = (
                data.get("action")
                or data.get("status")
                or data.get("reason")
                or str(data)
                or "ACTIVE"
            )

            column.markdown(
                metric_card(
                    name,
                    str(agent_status)[:28],
                    "Agent output"
                ),
                unsafe_allow_html=True
            )

        st.markdown(
            '<div class="section-title">'
            '📈 Live Charging Behaviour'
            '</div>',
            unsafe_allow_html=True
        )

        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            st.markdown(
                "**🔋 SOC & Battery Temperature**"
            )

            st.plotly_chart(
                make_soc_temperature_chart(df),
                use_container_width=True,
                config={
                    "displayModeBar": False
                }
            )

        with chart_col2:
            st.markdown(
                "**⚡ Charging Current & Grid Load**"
            )

            st.plotly_chart(
                make_current_grid_chart(df),
                use_container_width=True,
                config={
                    "displayModeBar": False
                }
            )

        st.markdown(
            '<div class="section-title">'
            '📡 Telemetry Records'
            '</div>',
            unsafe_allow_html=True
        )

        preferred_columns = [
            "step",
            "simulation_time",
            "soc",
            "target_soc",
            "temperature",
            "current",
            "grid_load",
            "state",
            "reason",
            "deadline_pressure",
            "available_minutes",
            "required_energy_kwh",
            "estimated_charging_minutes",
            "energy_kwh",
            "step_cost",
            "total_cost",
            "tariff_period",
            "tariff_rate"
        ]

        available_columns = [
            column
            for column in preferred_columns
            if column in df.columns
        ]

        st.dataframe(
            df[available_columns].tail(10),
            use_container_width=True,
            hide_index=True
        )

        csv_data = df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            "📥 Export Telemetry CSV",
            csv_data,
            "ev_charging_telemetry.csv",
            "text/csv"
        )

        if location:
            st.caption(
                f'📍 {location.get("display_name", "Current Location")}'
                f' | Latitude: {latitude:.6f}'
                f' | Longitude: {longitude:.6f}'
            )

        st.caption(
            "Research prototype: battery, thermal, grid and tariff "
            "thresholds are simulation parameters. Grid values may be "
            "estimated/simulated when live telemetry is unavailable, "
            "and tariff values are project simulation parameters."
        )

        if not st.session_state.running:
            st.markdown(
                '<div class="section-title">'
                '🏁 Charging Session Summary'
                '</div>',
                unsafe_allow_html=True
            )

            final = records[-1]

            final_soc = safe_float(
                value(final, "soc")
            )

            total_energy = safe_float(
                value(final, "total_energy_kwh")
            )

            final_cost = safe_float(
                value(final, "total_cost")
            )

            cols = st.columns(4)

            cols[0].metric(
                "Final SOC",
                f"{final_soc:.1f}%"
            )

            cols[1].metric(
                "Energy Consumed",
                f"{total_energy:.2f} kWh"
            )

            cols[2].metric(
                "Total Cost",
                money(final_cost)
            )

            cols[3].metric(
                "Departure Status",
                (
                    "READY"
                    if final_soc >= target_soc
                    else "TARGET NOT REACHED"
                )
            )

    live_dashboard()
