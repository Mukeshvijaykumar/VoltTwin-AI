import os
import sys

from datetime import (
    datetime,
    date,
    time as dt_time,
    timedelta
)

import pandas as pd
import streamlit as st

from streamlit_geolocation import (
    streamlit_geolocation
)


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if PROJECT_ROOT not in sys.path:

    sys.path.insert(
        0,
        PROJECT_ROOT
    )


# ============================================================
# PROJECT IMPORTS
# ============================================================

from simulation.charging_controller import (
    ChargingController
)

from services.location_service import (
    LocationService
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(

    page_title=
        "AI Smart EV Charging",

    page_icon=
        "🔋",

    layout=
        "wide",

    initial_sidebar_state=
        "expanded"
)


# ============================================================
# CONSTANTS
# ============================================================

SIMULATION_UPDATE_SECONDS = 0.5


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 38px;
        font-weight: 700;
        text-align: center;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        font-size: 18px;
        color: #777;
        margin-bottom: 25px;
    }

    .section-title {
        font-size: 24px;
        font-weight: 600;
        margin-top: 20px;
        margin-bottom: 10px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SESSION STATE
# ============================================================

defaults = {

    "controller":
        None,

    "records":
        [],

    "charging_started":
        False,

    "simulation_finished":
        False,

    "latitude":
        None,

    "longitude":
        None,

    "gps_accuracy":
        None,

    "location_data":
        None,

    "gps_error":
        None,

    "start_time":
        None
}


for key, value in defaults.items():

    if key not in st.session_state:

        st.session_state[key] = value


# ============================================================
# HELPER
# ============================================================

def get_value(
    record,
    *keys,
    default=0
):

    if not isinstance(
        record,
        dict
    ):

        return default

    for key in keys:

        if key in record:

            value = record[key]

            if value is not None:

                return value

    return default


# ============================================================
# SAFE FLOAT
# ============================================================

def safe_float(
    value,
    default=0.0
):

    try:

        return float(value)

    except (
        TypeError,
        ValueError
    ):

        return default


# ============================================================
# REVERSE GEOCODING
# ============================================================

@st.cache_data(
    ttl=300,
    show_spinner=False
)
def reverse_geocode(
    latitude,
    longitude
):

    try:

        service = LocationService()

        return service.reverse_geocode(
            latitude,
            longitude
        )

    except Exception as error:

        return {

            "latitude":
                latitude,

            "longitude":
                longitude,

            "locality":
                "GPS Location",

            "city":
                "",

            "district":
                "",

            "state":
                "",

            "country":
                "India",

            "display_name":
                "GPS Location",

            "error":
                str(error)
        }


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title(
        "⚙️ Charging Configuration"
    )

    st.caption(
        "Configure the charging requirement. "
        "The Digital Twin battery state is "
        "managed automatically by the controller."
    )

    # ========================================================
    # TARGET SOC
    # ========================================================

    st.markdown(
        "### 🔋 Charging Requirement"
    )

    required_soc = st.slider(

        "Target SOC (%)",

        min_value=50,

        max_value=100,

        value=90,

        step=1
    )

    # ========================================================
    # DEPARTURE
    # ========================================================

    st.markdown(
        "### 🕐 Departure Requirement"
    )

    departure_date = st.date_input(

        "Departure Date",

        value=date.today()
    )

    departure_time = st.time_input(

        "Departure Time",

        value=dt_time(
            18,
            0
        )
    )

    departure_datetime = (
        datetime.combine(
            departure_date,
            departure_time
        )
    )

    # If today's selected time has already
    # passed, automatically use tomorrow.

    if (

        departure_date == date.today()

        and

        departure_datetime
        <= datetime.now()

    ):

        departure_datetime = (
            departure_datetime
            + timedelta(days=1)
        )

    # ========================================================
    # LOCATION
    # ========================================================

    st.markdown("---")

    st.markdown(
        "### 📍 Vehicle Location"
    )

    st.caption(
        "Click the location button and "
        "allow browser location access."
    )

    location = (
        streamlit_geolocation()
    )

    # ========================================================
    # PROCESS GPS
    # ========================================================

    if (

        isinstance(
            location,
            dict
        )

        and

        location.get(
            "latitude"
        ) is not None

        and

        location.get(
            "longitude"
        ) is not None

    ):

        latitude = float(
            location["latitude"]
        )

        longitude = float(
            location["longitude"]
        )

        accuracy = location.get(
            "accuracy"
        )

        if accuracy is not None:

            accuracy = float(
                accuracy
            )

        st.session_state.latitude = (
            latitude
        )

        st.session_state.longitude = (
            longitude
        )

        st.session_state.gps_accuracy = (
            accuracy
        )

        st.session_state.gps_error = None

        st.session_state.location_data = (
            reverse_geocode(
                latitude,
                longitude
            )
        )

    # ========================================================
    # GPS ERROR
    # ========================================================

    elif (

        isinstance(
            location,
            dict
        )

        and

        location.get(
            "error"
        )

    ):

        error = location.get(
            "error"
        )

        if isinstance(
            error,
            dict
        ):

            st.session_state.gps_error = (
                error.get(
                    "message",
                    "Location unavailable"
                )
            )

        else:

            st.session_state.gps_error = (
                str(error)
            )

    # ========================================================
    # SHOW LOCATION
    # ========================================================

    if (

        st.session_state.latitude
        is not None

        and

        st.session_state.longitude
        is not None

    ):

        st.success(
            "📍 GPS Location Detected"
        )

        st.write(
            "Latitude: "
            f"{st.session_state.latitude:.7f}"
        )

        st.write(
            "Longitude: "
            f"{st.session_state.longitude:.7f}"
        )

        if (
            st.session_state.gps_accuracy
            is not None
        ):

            st.caption(
                "Reported GPS accuracy: "
                f"±{st.session_state.gps_accuracy:.1f} m"
            )

        if (
            st.session_state.location_data
        ):

            st.caption(
                st.session_state
                .location_data
                .get(
                    "display_name",
                    "GPS Location"
                )
            )

    else:

        st.warning(
            "Waiting for GPS location..."
        )

        if (
            st.session_state.gps_error
        ):

            st.error(
                st.session_state.gps_error
            )

    # ========================================================
    # RESET
    # ========================================================

    st.markdown("---")

    reset = st.button(

        "🔄 Reset Simulation",

        use_container_width=True
    )


# ============================================================
# RESET
# ============================================================

if reset:

    st.session_state.controller = None

    st.session_state.records = []

    st.session_state.charging_started = False

    st.session_state.simulation_finished = False

    st.session_state.start_time = None

    st.rerun()


# ============================================================
# HEADER
# ============================================================

st.markdown(

    '<div class="main-title">'
    '🔋 AI Smart EV Charging Control Center'
    '</div>',

    unsafe_allow_html=True
)

st.markdown(

    '<div class="subtitle">'
    'Multi-Agent AI • Digital Twin • '
    'Virtual Smart Charger • Deadline-Aware Charging'
    '</div>',

    unsafe_allow_html=True
)

st.divider()


# ============================================================
# INITIAL DASHBOARD
# ============================================================

if not st.session_state.charging_started:

    st.markdown(

        '<div class="section-title">'
        '🔋 Vehicle & Charging Requirement'
        '</div>',

        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # DO NOT SHOW INITIAL SOC
    #
    # Digital Twin Battery owns its own state.
    # --------------------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Target SOC",
            f"{required_soc}%"
        )

    with col2:

        st.metric(

            "Departure",

            departure_datetime.strftime(
                "%d-%m-%Y %I:%M %p"
            )
        )

    with col3:

        if (
            st.session_state.latitude
            is not None
        ):

            gps_status = "READY"

        else:

            gps_status = "WAITING"

        st.metric(
            "GPS Status",
            gps_status
        )

    # ========================================================
    # LOCATION
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '📍 Vehicle Location'
        '</div>',
        unsafe_allow_html=True
    )

    if (
        st.session_state.location_data
    ):

        location_name = (
            st.session_state
            .location_data
            .get(
                "display_name",
                "GPS Location"
            )
        )

        st.success(
            location_name
        )

    else:

        st.info(
            "Allow GPS location access "
            "before starting charging."
        )

    st.markdown("---")

    # ========================================================
    # START BUTTON
    # ========================================================

    st.markdown(

        """
        <div style="
            text-align:center;
            font-size:18px;
            font-weight:600;
            margin-bottom:10px;
        ">
        Ready to start the intelligent charging controller
        </div>
        """,

        unsafe_allow_html=True
    )

    start = st.button(

        "🚀 START INTELLIGENT CHARGING",

        type="primary",

        use_container_width=True
    )

    # ========================================================
    # START
    # ========================================================

    if start:

        if (

            st.session_state.latitude
            is None

            or

            st.session_state.longitude
            is None

        ):

            st.error(

                "📍 GPS location is required. "
                "Click the location button in the sidebar, "
                "allow location access, and press START."
            )

        else:

            try:

                controller = (
                    ChargingController(

                        target_soc=
                            float(
                                required_soc
                            ),

                        departure_time=
                            departure_datetime
                    )
                )

                # IMPORTANT:
                #
                # NO:
                # controller.battery.soc = ...
                #
                # NO:
                # controller.battery.temperature = ...
                #
                # NO:
                # controller.battery.health = ...
                #
                # The Battery class is the source
                # of the Digital Twin initial state.

                st.session_state.controller = (
                    controller
                )

                st.session_state.records = []

                st.session_state.charging_started = True

                st.session_state.simulation_finished = False

                st.session_state.start_time = (
                    datetime.now()
                )

                st.rerun()

            except Exception as error:

                st.error(
                    "Unable to start charging controller."
                )

                st.exception(error)

    st.stop()


# ============================================================
# CONTROLLER
# ============================================================

controller = (
    st.session_state.controller
)


if controller is None:

    st.error(
        "Charging controller is not initialized."
    )

    st.stop()


# ============================================================
# LIVE SIMULATION FRAGMENT
# ============================================================

run_every = (

    SIMULATION_UPDATE_SECONDS

    if not st.session_state.simulation_finished

    else None
)


@st.fragment(
    run_every=run_every,
    
)
def charging_simulation():

    # ========================================================
    # ONE SIMULATION CYCLE
    # ========================================================

    if not st.session_state.simulation_finished:

        try:

            record = controller.run_cycle(

                st.session_state.latitude,

                st.session_state.longitude

            )

            if record is None:

                record = {}

            st.session_state.records.append(
                record
            )

        except Exception as error:

            st.error(
                "❌ Charging controller error"
            )

            st.exception(error)

            return

    # ========================================================
    # RECORDS
    # ========================================================

    records = (
        st.session_state.records
    )

    if not records:

        st.warning(
            "No telemetry records available."
        )

        return

    latest = records[-1]

    df = pd.DataFrame(
        records
    )

    # ========================================================
    # STATUS
    # ========================================================

    status = get_value(

        latest,

        "Status",

        "status",

        default="RUNNING"
    )

    # ========================================================
    # TERMINAL STATUS
    # ========================================================

    if status in [

        "COMPLETED",

        "DEADLINE_MISSED"

    ]:

        st.session_state.simulation_finished = True

    # ========================================================
    # STATUS MESSAGE
    # ========================================================

    if status == "COMPLETED":

        st.success(
            "✅ Charging completed — "
            "target SOC reached."
        )

    elif status == "DEADLINE_MISSED":

        st.error(
            "⚠️ Departure deadline reached "
            "before target SOC was achieved."
        )

    elif status == "COOLING":

        st.warning(
            "🌡️ Battery cooling active — "
            "automatic charging restart enabled."
        )

    elif status in [

        "WAITING_GRID",

        "GRID_WAIT"

    ]:

        st.warning(
            "⚡ Grid demand is high — "
            "charging is temporarily waiting."
        )

    elif status in [

        "WAITING",

        "SOLAR_WAIT"

    ]:

        st.info(
            "⏳ Intelligent controller is waiting "
            "for better charging conditions."
        )

    else:

        st.info(
            "🔄 Intelligent charging controller running..."
        )

    # ========================================================
    # VEHICLE / DIGITAL TWIN
    # ========================================================

    st.markdown(

        '<div class="section-title">'
        '🔋 Digital Twin Battery'
        '</div>',

        unsafe_allow_html=True
    )

    soc = safe_float(

        get_value(

            latest,

            "SOC",

            "soc",

            default=0
        )
    )

    temperature = safe_float(

        get_value(

            latest,

            "Temperature",

            "temperature",

            default=0
        )
    )

    health = safe_float(

        get_value(

            latest,

            "Health",

            "health",

            default=0
        )
    )

    current = safe_float(

        get_value(

            latest,

            "Decision_Current",

            "Current",

            "current",

            default=0
        )
    )

    voltage = safe_float(

        get_value(

            latest,

            "Voltage",

            "voltage",

            default=230
        )
    )

    power = safe_float(

        get_value(

            latest,

            "Power_kW",

            "power_kw",

            "Charger_Power_kW",

            default=0
        )
    )

    col1, col2, col3, col4, col5 = (
        st.columns(5)
    )

    with col1:

        st.metric(

            "SOC",

            f"{soc:.1f}%",

            f"Target {required_soc}%"
        )

    with col2:

        st.metric(

            "Temperature",

            f"{temperature:.1f} °C"
        )

    with col3:

        st.metric(

            "Health",

            f"{health:.1f}%"
        )

    with col4:

        st.metric(

            "Current",

            f"{current:.1f} A"
        )

    with col5:

        st.metric(

            "Power",

            f"{power:.2f} kW"
        )

    # ========================================================
    # OPERATING CONDITIONS
    # ========================================================

    st.markdown(

        '<div class="section-title">'
        '🌐 Live Operating Conditions'
        '</div>',

        unsafe_allow_html=True
    )

    weather_temperature = safe_float(

        get_value(

            latest,

            "Weather_Temperature",

            "weather_temperature",

            "temperature_2m",

            default=0
        )
    )

    humidity = safe_float(

        get_value(

            latest,

            "Humidity",

            "humidity",

            default=0
        )
    )

    cloud = safe_float(

        get_value(

            latest,

            "Cloud_Cover",

            "cloud_cover",

            default=0
        )
    )

    wind = safe_float(

        get_value(

            latest,

            "Wind_Speed",

            "wind_speed",

            default=0
        )
    )

    grid_load = safe_float(

        get_value(

            latest,

            "Grid_Load",

            "grid_load",

            default=0
        )
    )

    col1, col2, col3, col4 = (
        st.columns(4)
    )

    with col1:

        st.metric(

            "🌡️ Weather",

            f"{weather_temperature:.1f} °C"
        )

    with col2:

        st.metric(

            "💧 Humidity",

            f"{humidity:.1f}%"
        )

    with col3:

        st.metric(

            "☁️ Cloud Cover",

            f"{cloud:.1f}%"
        )

    with col4:

        st.metric(

            "💨 Wind",

            f"{wind:.1f} km/h"
        )

    # ========================================================
    # GRID / SOLAR
    # ========================================================

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            "### ⚡ Grid Status"
        )

        st.metric(

            "Grid Load",

            f"{grid_load:.1f}%"
        )

        if grid_load >= 90:

            st.error(
                "🔴 CRITICAL GRID LOAD"
            )

        elif grid_load >= 75:

            st.warning(
                "🟠 HIGH GRID DEMAND"
            )

        else:

            st.success(
                "🟢 GRID STABLE"
            )

    with col2:

        st.markdown(
            "### ☀️ Solar Availability"
        )

        st.metric(

            "Cloud Cover",

            f"{cloud:.1f}%"
        )

        if cloud < 30:

            st.success(
                "🟢 HIGH SOLAR AVAILABILITY"
            )

        elif cloud < 70:

            st.warning(
                "🟡 MEDIUM SOLAR AVAILABILITY"
            )

        else:

            st.info(
                "🔵 LOW SOLAR AVAILABILITY"
            )

    # ========================================================
    # AI COORDINATOR
    # ========================================================

    st.divider()

    st.markdown(

        '<div class="section-title">'
        '🧠 AI Coordinator Decision'
        '</div>',

        unsafe_allow_html=True
    )

    decision_action = get_value(

        latest,

        "Action",

        "action",

        default="UNKNOWN"
    )

    decision_current = safe_float(

        get_value(

            latest,

            "Decision_Current",

            "current",

            "Current",

            default=0
        )
    )

    decision_mode = get_value(

        latest,

        "Decision_Mode",

        "mode",

        default="IDLE"
    )

    reason = get_value(

        latest,

        "Decision_Reason",

        "reason",

        default=""
    )

    col1, col2, col3 = (
        st.columns(3)
    )

    with col1:

        st.metric(

            "AI Action",

            str(decision_action)
        )

    with col2:

        st.metric(

            "Recommended Current",

            f"{decision_current:.1f} A"
        )

    with col3:

        st.metric(

            "Charging Mode",

            str(decision_mode)
        )

    st.info(
        f"💡 Decision Reason: {reason}"
    )

    # ========================================================
    # DEADLINE SCHEDULER
    # ========================================================

    pressure = get_value(

        latest,

        "Deadline_Pressure",

        "deadline_pressure",

        default="LOW"
    )

    simulation_minutes = safe_float(

        get_value(

            latest,

            "Simulation_Minutes",

            "simulation_minutes",

            default=0
        )
    )

    required_energy = safe_float(

        get_value(

            latest,

            "Required_Energy_kWh",

            "required_energy_kwh",

            default=0
        )
    )

    available_minutes = safe_float(

        get_value(

            latest,

            "Available_Minutes",

            "available_minutes",

            default=0
        )
    )

    estimated_minutes = safe_float(

        get_value(

            latest,

            "Estimated_Charging_Minutes",

            "estimated_charging_minutes",

            default=0
        )
    )

    st.markdown(
        "### 🕐 Deadline-Aware Scheduler"
    )

    col1, col2, col3, col4 = (
        st.columns(4)
    )

    with col1:

        st.metric(

            "Deadline Pressure",

            str(pressure)
        )

    with col2:

        st.metric(

            "Required Energy",

            f"{required_energy:.2f} kWh"
        )

    with col3:

        st.metric(

            "Available Time",

            f"{available_minutes / 60:.2f} h"
        )

    with col4:

        st.metric(

            "Estimated Charge",

            f"{estimated_minutes / 60:.2f} h"
        )

    # ========================================================
    # SIMULATION CLOCK
    # ========================================================

    simulation_time_text = get_value(

        latest,

        "Simulation_Time",

        "simulation_time",

        default=""
    )

    st.markdown(
        "### ⏱️ Automatic Simulation Clock"
    )

    col1, col2, col3 = (
        st.columns(3)
    )

    with col1:

        st.metric(

            "Simulation Elapsed",

            f"{simulation_minutes / 60:.2f} h"
        )

    with col2:

        st.metric(

            "Simulation Time",

            str(simulation_time_text)
        )

    with col3:

        st.metric(

            "Departure",

            departure_datetime.strftime(
                "%d-%m-%Y %I:%M %p"
            )
        )

    # ========================================================
    # VIRTUAL SMART CHARGER
    # ========================================================

    st.markdown(
        "### 🔌 Virtual Smart Charger"
    )

    charger_status = get_value(

        latest,

        "Charger_Status",

        "charger_status",

        default="IDLE"
    )

    charger_mode = get_value(

        latest,

        "Charger_Mode",

        "charger_mode",

        default="IDLE"
    )

    col1, col2, col3, col4 = (
        st.columns(4)
    )

    with col1:

        st.metric(

            "Status",

            str(charger_status)
        )

    with col2:

        st.metric(

            "Current",

            f"{current:.1f} A"
        )

    with col3:

        st.metric(

            "Voltage",

            f"{voltage:.1f} V"
        )

    with col4:

        st.metric(

            "Mode",

            str(charger_mode)
        )

    # ========================================================
    # MULTI AGENT LAYER
    # ========================================================

    with st.expander(
        "🤖 Multi-Agent Decision Layer"
    ):

        col1, col2, col3, col4, col5 = (
            st.columns(5)
        )

        with col1:

            st.markdown(
                "### 🔋 Battery Agent"
            )

            st.write(

                get_value(

                    latest,

                    "Battery_Action",

                    "battery_action",

                    default="N/A"
                )
            )

        with col2:

            st.markdown(
                "### ⚡ Grid Agent"
            )

            st.write(

                get_value(

                    latest,

                    "Grid_Action",

                    "grid_action",

                    default="N/A"
                )
            )

        with col3:

            st.markdown(
                "### ☀️ Solar Agent"
            )

            st.write(

                get_value(

                    latest,

                    "Solar_Action",

                    "solar_action",

                    default="N/A"
                )
            )

        with col4:

            st.markdown(
                "### 💰 Tariff Agent"
            )

            st.write(

                get_value(

                    latest,

                    "Tariff_Action",

                    "tariff_action",

                    default="N/A"
                )
            )

        with col5:

            st.markdown(
                "### 👤 User Agent"
            )

            st.write(

                get_value(

                    latest,

                    "User_Action",

                    "user_action",

                    default="N/A"
                )
            )

    # ========================================================
    # COOLING / RESTART
    # ========================================================

    cooling_active = get_value(

        latest,

        "Cooling_Active",

        "cooling_active",

        default=False
    )

    cooling_cycles = safe_float(

        get_value(

            latest,

            "Cooling_Cycles",

            "cooling_cycles",

            default=0
        )
    )

    restart_count = safe_float(

        get_value(

            latest,

            "Restart_Count",

            "restart_count",

            default=0
        )
    )

    st.markdown(
        "### 🌡️ Thermal Protection"
    )

    col1, col2, col3 = (
        st.columns(3)
    )

    with col1:

        st.metric(

            "Cooling",

            "ACTIVE"
            if cooling_active
            else "NORMAL"
        )

    with col2:

        st.metric(

            "Cooling Cycles",

            int(cooling_cycles)
        )

    with col3:

        st.metric(

            "Automatic Restarts",

            int(restart_count)
        )

    # ========================================================
    # GRAPHS
    # ========================================================

    st.divider()

    st.markdown(
        "### 📈 SOC & Battery Temperature"
    )

    graph_rows = []

    for item in records:

        graph_rows.append({

            "Simulation Hours":

                safe_float(

                    get_value(

                        item,

                        "Simulation_Minutes",

                        "simulation_minutes",

                        default=0
                    )

                ) / 60.0,

            "SOC (%)":

                safe_float(

                    get_value(

                        item,

                        "SOC",

                        "soc",

                        default=0
                    )
                ),

            "Temperature (°C)":

                safe_float(

                    get_value(

                        item,

                        "Temperature",

                        "temperature",

                        default=0
                    )
                )
        })

    graph_df = pd.DataFrame(
        graph_rows
    )

    if not graph_df.empty:

        graph_df = (
            graph_df
            .set_index(
                "Simulation Hours"
            )
        )

        st.line_chart(

            graph_df[
                [
                    "SOC (%)",
                    "Temperature (°C)"
                ]
            ],

            height=300
        )

    # ========================================================
    # GRAPH 2
    # ========================================================

    st.markdown(
        "### ⚡ Charging Current & Grid Load"
    )

    graph_rows = []

    for item in records:

        graph_rows.append({

            "Simulation Hours":

                safe_float(

                    get_value(

                        item,

                        "Simulation_Minutes",

                        "simulation_minutes",

                        default=0
                    )

                ) / 60.0,

            "Charging Current (A)":

                safe_float(

                    get_value(

                        item,

                        "Decision_Current",

                        "Current",

                        "current",

                        default=0
                    )
                ),

            "Grid Load (%)":

                safe_float(

                    get_value(

                        item,

                        "Grid_Load",

                        "grid_load",

                        default=0
                    )
                )
        })

    graph_df = pd.DataFrame(
        graph_rows
    )

    if not graph_df.empty:

        graph_df = (
            graph_df
            .set_index(
                "Simulation Hours"
            )
        )

        st.line_chart(

            graph_df[
                [
                    "Charging Current (A)",
                    "Grid Load (%)"
                ]
            ],

            height=300
        )

    # ========================================================
    # TELEMETRY
    # ========================================================

    with st.expander(
        "📊 Telemetry Records"
    ):

        st.dataframe(

            df,

            use_container_width=True,

            height=300
        )

    # ========================================================
    # DOWNLOAD
    # ========================================================

    with st.expander(
        "📥 Export Telemetry"
    ):

        csv_data = (

            df
            .to_csv(
                index=False
            )
            .encode(
                "utf-8"
            )
        )

        st.download_button(

            "Download Charging Telemetry",

            data=csv_data,

            file_name=
                "ev_charging_telemetry.csv",

            mime=
                "text/csv",

            use_container_width=True
        )

    # ========================================================
    # LOCATION
    # ========================================================

    if (
        st.session_state.location_data
    ):

        st.caption(

            "📍 "
            +
            st.session_state
            .location_data
            .get(
                "display_name",
                "GPS Location"
            )
            +
            " | Latitude: "
            +
            f"{st.session_state.latitude:.7f}"
            +
            " | Longitude: "
            +
            f"{st.session_state.longitude:.7f}"
        )

    # ========================================================
    # RESEARCH NOTE
    # ========================================================

    st.caption(

        "Research prototype: battery, thermal, "
        "grid and tariff thresholds are simulation "
        "parameters and are not universal real-world "
        "EV safety limits or official electricity tariffs."
    )

    # ========================================================
    # STOP STREAMING
    # ========================================================

    if status in [

        "COMPLETED",

        "DEADLINE_MISSED"

    ]:

        st.success(
            "Simulation stopped."
        )


# ============================================================
# RUN
# ============================================================

charging_simulation()