import json
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px


# =========================================================
# CONFIGURATION
# =========================================================

ACTIVITY_ID = "82378787c4a8d15133fd63519993cd75"
JSON_FILE = "fortyguard_result.json"


# =========================================================
# STREAMLIT CONFIG
# =========================================================

st.set_page_config(
    page_title="Urban HeatGuard",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #0b1120;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    max-width: 1500px;
}

/* SIDEBAR */

section[data-testid="stSidebar"] {
    background: #111827;
    border-right: 1px solid #263244;
}

section[data-testid="stSidebar"] * {
    color: #e5e7eb;
}

/* HERO */

.hero {
    background: linear-gradient(
        135deg,
        #111827 0%,
        #172554 55%,
        #7f1d1d 100%
    );

    border: 1px solid #263244;
    border-radius: 22px;

    padding: 32px 36px;

    margin-bottom: 25px;

    box-shadow: 0 12px 40px rgba(0,0,0,0.25);
}

.hero-title {
    font-size: 42px;
    font-weight: 800;
    color: white;
    margin-bottom: 5px;
}

.hero-subtitle {
    font-size: 17px;
    color: #cbd5e1;
    margin-bottom: 20px;
}

.badge {
    display: inline-block;

    padding: 7px 14px;

    border-radius: 30px;

    background: rgba(255,255,255,0.10);

    border: 1px solid rgba(255,255,255,0.15);

    color: #e2e8f0;

    font-size: 13px;
}

/* KPI */

.kpi {
    background: #111827;

    border: 1px solid #263244;

    border-radius: 18px;

    padding: 22px;

    min-height: 145px;

    box-shadow: 0 8px 25px rgba(0,0,0,0.18);
}

.kpi-label {
    color: #94a3b8;

    font-size: 14px;

    font-weight: 600;
}

.kpi-value {
    color: white;

    font-size: 30px;

    font-weight: 800;

    margin-top: 10px;
}

.kpi-small {
    color: #64748b;

    font-size: 12px;

    margin-top: 5px;
}

/* SECTION */

.section-title {
    font-size: 25px;

    font-weight: 800;

    color: white;

    margin-top: 30px;

    margin-bottom: 5px;
}

.section-subtitle {
    color: #94a3b8;

    margin-bottom: 18px;
}

/* RISK CARD */

.risk-card {
    border-radius: 18px;

    padding: 20px;

    background: #111827;

    border: 1px solid #263244;

    text-align: center;
}

.risk-number {
    font-size: 32px;

    font-weight: 800;

    color: white;
}

.risk-label {
    font-size: 14px;

    color: #94a3b8;
}

/* ACTION CARD */

.action-card {
    background: #111827;

    border: 1px solid #263244;

    border-radius: 18px;

    padding: 24px;

    margin-bottom: 15px;
}

.action-title {
    font-size: 19px;

    font-weight: 700;

    color: white;

    margin-bottom: 10px;
}

.action-text {
    color: #cbd5e1;

    line-height: 1.8;
}

/* FOOTER */

.footer {
    margin-top: 50px;

    padding: 25px;

    border-top: 1px solid #263244;

    text-align: center;

    color: #64748b;

    font-size: 13px;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# LOAD FORTYGUARD DATA
# =========================================================

@st.cache_data
def load_heatmap_data():

    with open(
        JSON_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    # Handle FortyGuard response structure

    if "data" in data:
        data = data["data"]

    if "result" in data:
        result = data["result"]
    else:
        result = data

    map_data = result["map_data"]

    features = map_data["features"]

    rows = []

    for feature in features:

        properties = feature["properties"]

        coordinates = feature["geometry"]["coordinates"][0]

        longitude = np.mean(
            [point[0] for point in coordinates]
        )

        latitude = np.mean(
            [point[1] for point in coordinates]
        )

        rows.append({

            "tile_id":
                properties["tile_id"],

            "latitude":
                latitude,

            "longitude":
                longitude,

            "average_temperature":
                properties["average_temperature"],

            "min_temperature":
                properties["min_temperature"],

            "max_temperature":
                properties["max_temperature"]

        })

    return pd.DataFrame(rows)


# =========================================================
# CALCULATE HEAT RISK
# =========================================================

def calculate_risk(df):

    df = df.copy()

    min_temp = df[
        "average_temperature"
    ].min()

    max_temp = df[
        "average_temperature"
    ].max()

    if max_temp == min_temp:

        df["risk_score"] = 0

    else:

        df["risk_score"] = (

            (
                df["average_temperature"]
                - min_temp
            )

            /

            (
                max_temp
                - min_temp
            )

        ) * 100

    def risk_level(score):

        if score >= 75:
            return "HIGH"

        elif score >= 50:
            return "MEDIUM"

        else:
            return "LOW"

    df["risk_level"] = (
        df["risk_score"]
        .apply(risk_level)
    )

    return df


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        "## 🌡️ HeatGuard"
    )

    st.caption(
        "Urban Heat Intelligence Platform"
    )

    st.divider()

    st.markdown(
        "### 📍 Dashboard"
    )

    page = st.radio(

        "Navigation",

        [
            "Overview",
            "Temperature Map",
            "Risk Analysis",
            "Hotspots",
            "Recommendations",
            "Data & Export"
        ],

        label_visibility="collapsed"
    )

    st.divider()

    st.markdown(
        "### ⚙️ System"
    )

    st.success(
        "● FortyGuard Data Connected"
    )

    st.caption(
        f"Activity ID:\n{ACTIVITY_ID}"
    )

    st.divider()

    st.caption(
        "Urban HeatGuard"
    )

    st.caption(
        "AI-Powered Urban Heat Intelligence"
    )


# =========================================================
# LOAD DATA
# =========================================================

try:

    with st.spinner(
        "Loading urban heat intelligence..."
    ):

        df = load_heatmap_data()

except FileNotFoundError:

    st.error(
        "❌ fortyguard_result.json was not found."
    )

    st.info(
        "Make sure fortyguard_result.json "
        "is in the same folder as app.py."
    )

    st.stop()

except Exception as e:

    st.error(
        f"❌ Error loading data: {e}"
    )

    st.stop()


# =========================================================
# CALCULATE RISK
# =========================================================

df = calculate_risk(df)


# =========================================================
# GLOBAL STATISTICS
# =========================================================

average_temp = (
    df["average_temperature"].mean()
)

minimum_temp = (
    df["average_temperature"].min()
)

maximum_temp = (
    df["average_temperature"].max()
)

high_risk = len(
    df[
        df["risk_level"] == "HIGH"
    ]
)

medium_risk = len(
    df[
        df["risk_level"] == "MEDIUM"
    ]
)

low_risk = len(
    df[
        df["risk_level"] == "LOW"
    ]
)

total_zones = len(df)

highest_zone = df.loc[
    df["average_temperature"].idxmax()
]


# =========================================================
# HERO HEADER
# =========================================================

st.markdown("""
<div class="hero">

<div class="hero-title">
🌡️ Urban HeatGuard
</div>

<div class="hero-subtitle">
AI-Powered Urban Heat Risk Detection & Spatial Intelligence
</div>

<span class="badge">
● FortyGuard Intelligence Connected
</span>

&nbsp;&nbsp;

<span class="badge">
🛰️ Spatial Temperature Analysis
</span>

</div>
""", unsafe_allow_html=True)


# =========================================================
# OVERVIEW
# =========================================================

if page == "Overview":

    st.markdown(
        '<div class="section-title">'
        '📊 Urban Heat Overview'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Monitor temperature conditions and identify urban heat hotspots.'
        '</div>',
        unsafe_allow_html=True
    )

    # -----------------------------------------------------
    # KPI CARDS
    # -----------------------------------------------------

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.markdown(
            f"""
            <div class="kpi">

            <div class="kpi-label">
            🌡️ Average Temperature
            </div>

            <div class="kpi-value">
            {average_temp:.2f}°C
            </div>

            <div class="kpi-small">
            Across all monitored zones
            </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:

        st.markdown(
            f"""
            <div class="kpi">

            <div class="kpi-label">
            🔥 Maximum Temperature
            </div>

            <div class="kpi-value">
            {maximum_temp:.2f}°C
            </div>

            <div class="kpi-small">
            Highest detected temperature
            </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with c3:

        st.markdown(
            f"""
            <div class="kpi">

            <div class="kpi-label">
            📍 Heat Zones
            </div>

            <div class="kpi-value">
            {total_zones:,}
            </div>

            <div class="kpi-small">
            Monitored spatial zones
            </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with c4:

        st.markdown(
            f"""
            <div class="kpi">

            <div class="kpi-label">
            🚨 High Risk Zones
            </div>

            <div class="kpi-value">
            {high_risk}
            </div>

            <div class="kpi-small">
            Need priority attention
            </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    # -----------------------------------------------------
    # RISK SUMMARY
    # -----------------------------------------------------

    st.markdown(
        '<div class="section-title">'
        '🚨 Heat Risk Summary'
        '</div>',
        unsafe_allow_html=True
    )

    r1, r2, r3 = st.columns(3)

    with r1:

        st.markdown(
            f"""
            <div class="risk-card">

            <div class="risk-number">
            🔴 {high_risk}
            </div>

            <div class="risk-label">
            HIGH RISK ZONES
            </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with r2:

        st.markdown(
            f"""
            <div class="risk-card">

            <div class="risk-number">
            🟠 {medium_risk}
            </div>

            <div class="risk-label">
            MEDIUM RISK ZONES
            </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with r3:

        st.markdown(
            f"""
            <div class="risk-card">

            <div class="risk-number">
            🟢 {low_risk}
            </div>

            <div class="risk-label">
            LOW RISK ZONES
            </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    if high_risk > 0:

        st.warning(
            f"⚠️ **{high_risk} high-risk zone(s)** detected. "
            "These locations should receive priority cooling measures."
        )

    else:

        st.success(
            "✅ No high-risk zones detected."
        )

    # -----------------------------------------------------
    # CHARTS
    # -----------------------------------------------------

    left, right = st.columns(2)

    with left:

        st.markdown(
            "### 🌡️ Temperature Distribution"
        )

        hist_fig = px.histogram(

            df,

            x="average_temperature",

            nbins=25,

            labels={
                "average_temperature":
                    "Temperature (°C)"
            }

        )

        hist_fig.update_layout(

            template="plotly_dark",

            paper_bgcolor="#111827",

            plot_bgcolor="#111827",

            margin=dict(
                l=10,
                r=10,
                t=20,
                b=10
            ),

            showlegend=False

        )

        st.plotly_chart(
            hist_fig,
            use_container_width=True
        )

    with right:

        st.markdown(
            "### 🚨 Risk Distribution"
        )

        risk_counts = (
            df["risk_level"]
            .value_counts()
            .reset_index()
        )

        risk_counts.columns = [
            "Risk Level",
            "Zones"
        ]

        pie_fig = px.pie(

            risk_counts,

            names="Risk Level",

            values="Zones",

            hole=0.55,

            color="Risk Level",

            color_discrete_map={

                "HIGH":
                    "#ef4444",

                "MEDIUM":
                    "#f59e0b",

                "LOW":
                    "#22c55e"

            }

        )

        pie_fig.update_layout(

            template="plotly_dark",

            paper_bgcolor="#111827",

            plot_bgcolor="#111827",

            margin=dict(
                l=10,
                r=10,
                t=20,
                b=10
            )

        )

        st.plotly_chart(
            pie_fig,
            use_container_width=True
        )


# =========================================================
# TEMPERATURE MAP
# =========================================================

elif page == "Temperature Map":

    st.markdown(
        '<div class="section-title">'
        '🗺️ Urban Heat Map'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Explore temperature levels and identify the hottest areas.'
        '</div>',
        unsafe_allow_html=True
    )

    # -----------------------------------------------------
    # MAP CONTROLS
    # -----------------------------------------------------

    map_col1, map_col2, map_col3 = st.columns(3)

    with map_col1:

        map_mode = st.selectbox(
            "Map View",
            [
                "Temperature",
                "Heat Risk"
            ]
        )

    with map_col2:

        marker_size = st.slider(
            "Marker Size",
            8,
            30,
            15
        )

    with map_col3:

        show_high_risk = st.checkbox(
            "Show Only High Risk",
            value=False
        )

    # -----------------------------------------------------
    # FILTER
    # -----------------------------------------------------

    map_df = df.copy()

    if show_high_risk:

        map_df = map_df[
            map_df["risk_level"] == "HIGH"
        ]

    # -----------------------------------------------------
    # TEMPERATURE MAP
    # -----------------------------------------------------

    if map_mode == "Temperature":

        fig = px.scatter_mapbox(

            map_df,

            lat="latitude",

            lon="longitude",

            color="average_temperature",

            size="average_temperature",

            size_max=marker_size,

            hover_name="tile_id",

            hover_data={

                "average_temperature":
                    ":.2f",

                "min_temperature":
                    ":.2f",

                "max_temperature":
                    ":.2f",

                "risk_score":
                    ":.1f",

                "risk_level":
                    True,

                "latitude":
                    ":.5f",

                "longitude":
                    ":.5f"

            },

            color_continuous_scale=[

                [0.00, "#2563eb"],

                [0.20, "#06b6d4"],

                [0.40, "#22c55e"],

                [0.60, "#facc15"],

                [0.80, "#f97316"],

                [1.00, "#dc2626"]

            ],

            zoom=13,

            height=720

        )

        fig.update_coloraxes(
            colorbar_title="Temperature (°C)"
        )

    # -----------------------------------------------------
    # HEAT RISK MAP
    # -----------------------------------------------------

    else:

        fig = px.scatter_mapbox(

            map_df,

            lat="latitude",

            lon="longitude",

            color="risk_level",

            size="risk_score",

            size_max=marker_size,

            hover_name="tile_id",

            hover_data={

                "average_temperature":
                    ":.2f",

                "min_temperature":
                    ":.2f",

                "max_temperature":
                    ":.2f",

                "risk_score":
                    ":.1f",

                "risk_level":
                    True

            },

            color_discrete_map={

                "LOW":
                    "#22c55e",

                "MEDIUM":
                    "#f59e0b",

                "HIGH":
                    "#ef4444"

            },

            zoom=13,

            height=720

        )

    # -----------------------------------------------------
    # MAP DESIGN
    # -----------------------------------------------------

    fig.update_layout(

        mapbox_style="open-street-map",

        mapbox=dict(

            center=dict(

                lat=df[
                    "latitude"
                ].mean(),

                lon=df[
                    "longitude"
                ].mean()

            ),

            zoom=13

        ),

        paper_bgcolor="#111827",

        plot_bgcolor="#111827",

        margin=dict(

            l=0,

            r=0,

            t=0,

            b=0

        ),

        font=dict(

            color="#e5e7eb"

        ),

        legend=dict(

            bgcolor="rgba(17,24,39,0.85)",

            bordercolor="#374151",

            borderwidth=1,

            font=dict(
                color="white"
            )

        )

    )

    # -----------------------------------------------------
    # SHOW MAP
    # -----------------------------------------------------

    st.plotly_chart(

        fig,

        use_container_width=True,

        config={

            "scrollZoom":
                True,

            "displaylogo":
                False,

            "modeBarButtonsToRemove": [

                "lasso2d",

                "select2d"

            ]

        }

    )

    # -----------------------------------------------------
    # MAP SUMMARY
    # -----------------------------------------------------

    st.markdown(
        "### 📍 Map Summary"
    )

    s1, s2, s3, s4 = st.columns(4)

    s1.metric(
        "🌡️ Average",
        f"{average_temp:.1f} °C"
    )

    s2.metric(
        "🔥 Hottest",
        f"{maximum_temp:.1f} °C"
    )

    s3.metric(
        "🚨 High Risk",
        f"{high_risk}"
    )

    s4.metric(
        "📍 Total Zones",
        f"{total_zones:,}"
    )

    # -----------------------------------------------------
    # HOTTEST LOCATION
    # -----------------------------------------------------

    st.markdown(
        "### 🔥 Hottest Detected Location"
    )

    h1, h2, h3 = st.columns(3)

    h1.metric(
        "Zone",
        str(
            highest_zone["tile_id"]
        )
    )

    h2.metric(
        "Temperature",
        f"{highest_zone['average_temperature']:.2f} °C"
    )

    h3.metric(
        "Risk",
        highest_zone["risk_level"]
    )

    st.info(
        "💡 **Tip:** Switch between Temperature and Heat Risk "
        "views. Hover over points to see detailed information."
    )


# =========================================================
# RISK ANALYSIS
# =========================================================

elif page == "Risk Analysis":

    st.markdown(
        '<div class="section-title">'
        '🔥 Heat Risk Analysis'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Understand which locations have the highest relative heat risk.'
        '</div>',
        unsafe_allow_html=True
    )

    # -----------------------------------------------------
    # RISK MAP
    # -----------------------------------------------------

    risk_map = px.scatter_mapbox(

        df,

        lat="latitude",

        lon="longitude",

        color="risk_level",

        size="risk_score",

        hover_name="tile_id",

        hover_data={

            "average_temperature":
                ":.2f",

            "min_temperature":
                ":.2f",

            "max_temperature":
                ":.2f",

            "risk_score":
                ":.1f",

            "risk_level":
                True

        },

        color_discrete_map={

            "LOW":
                "#22c55e",

            "MEDIUM":
                "#f59e0b",

            "HIGH":
                "#ef4444"

        },

        zoom=13,

        height=680

    )

    risk_map.update_layout(

        mapbox_style="open-street-map",

        template="plotly_dark",

        paper_bgcolor="#111827",

        plot_bgcolor="#111827",

        margin=dict(
            l=0,
            r=0,
            t=0,
            b=0
        )

    )

    st.plotly_chart(
        risk_map,
        use_container_width=True
    )

    # -----------------------------------------------------
    # RISK SCORE DISTRIBUTION
    # -----------------------------------------------------

    st.markdown(
        "### 📊 Risk Score Distribution"
    )

    risk_chart = px.histogram(

        df,

        x="risk_score",

        nbins=20,

        labels={
            "risk_score":
                "Risk Score"
        }

    )

    risk_chart.update_layout(

        template="plotly_dark",

        paper_bgcolor="#111827",

        plot_bgcolor="#111827"

    )

    st.plotly_chart(
        risk_chart,
        use_container_width=True
    )


# =========================================================
# HOTSPOTS
# =========================================================

elif page == "Hotspots":

    st.markdown(
        '<div class="section-title">'
        '🔥 Urban Heat Hotspots'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">'
        'The hottest locations ranked by heat risk.'
        '</div>',
        unsafe_allow_html=True
    )

    number = st.slider(

        "Number of hotspots",

        5,

        min(
            50,
            total_zones
        ),

        10

    )

    hotspots = (

        df

        .sort_values(
            "risk_score",
            ascending=False
        )

        .head(number)

        .copy()

    )

    hotspots["Priority"] = range(
        1,
        len(hotspots) + 1
    )

    display_df = hotspots[

        [
            "Priority",

            "tile_id",

            "latitude",

            "longitude",

            "average_temperature",

            "min_temperature",

            "max_temperature",

            "risk_score",

            "risk_level"

        ]

    ].copy()

    display_df.columns = [

        "Priority",

        "Zone",

        "Latitude",

        "Longitude",

        "Average °C",

        "Minimum °C",

        "Maximum °C",

        "Risk Score",

        "Risk Level"

    ]

    st.dataframe(

        display_df,

        use_container_width=True,

        hide_index=True

    )

    st.markdown(
        "### 🔥 Hottest Detected Zone"
    )

    st.metric(

        "Hottest Zone",

        highest_zone["tile_id"],

        f"{highest_zone['average_temperature']:.2f} °C"

    )


# =========================================================
# RECOMMENDATIONS
# =========================================================

elif page == "Recommendations":

    st.markdown(
        '<div class="section-title">'
        '💡 Recommendations'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Simple recommendations for reducing heat in high-risk areas.'
        '</div>',
        unsafe_allow_html=True
    )

    # -----------------------------------------------------
    # OVERALL STATUS
    # -----------------------------------------------------

    if high_risk >= 20:

        st.error(

            f"🔴 **Critical:** {high_risk} high-risk zones "
            "need immediate attention."

        )

    elif high_risk > 0:

        st.warning(

            f"🟠 **Attention Needed:** {high_risk} high-risk "
            "zones have been detected."

        )

    else:

        st.success(
            "🟢 **Good:** No high-risk zones were detected."
        )

    # -----------------------------------------------------
    # RECOMMENDATIONS
    # -----------------------------------------------------

    a1, a2 = st.columns(2)

    with a1:

        st.markdown(
            """
            <div class="action-card">

            <div class="action-title">
            🌳 Plant More Trees
            </div>

            <div class="action-text">

            • Increase tree coverage<br>

            • Add green spaces<br>

            • Protect existing trees<br>

            • Focus on high-risk areas

            </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with a2:

        st.markdown(
            """
            <div class="action-card">

            <div class="action-title">
            🏠 Add More Shade
            </div>

            <div class="action-text">

            • Add shaded walking areas<br>

            • Cover public waiting areas<br>

            • Improve shade near roads<br>

            • Protect people from direct sunlight

            </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    a3, a4 = st.columns(2)

    with a3:

        st.markdown(
            """
            <div class="action-card">

            <div class="action-title">
            💧 Cooling & Water
            </div>

            <div class="action-text">

            • Add drinking water stations<br>

            • Create public cooling points<br>

            • Support vulnerable people<br>

            • Improve heat-response services

            </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with a4:

        st.markdown(
            """
            <div class="action-card">

            <div class="action-title">
            🛣️ Improve Urban Surfaces
            </div>

            <div class="action-text">

            • Use reflective materials<br>

            • Consider cool roofs<br>

            • Reduce heat-absorbing surfaces<br>

            • Improve exposed infrastructure

            </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    # -----------------------------------------------------
    # RESOURCE RECOMMENDATIONS
    # -----------------------------------------------------

    st.markdown(
        "### 🏗️ Recommended Resources"
    )

    rc1, rc2, rc3 = st.columns(3)

    rc1.metric(
        "🌳 Tree / Green Areas",
        f"{high_risk} zones"
    )

    rc2.metric(
        "💧 Cooling Stations",
        f"{high_risk} zones"
    )

    rc3.metric(
        "🏠 Shade Structures",
        f"{high_risk + medium_risk} zones"
    )

    st.info(
        "💡 **Recommendation:** Start with the highest-risk "
        "locations and gradually expand cooling measures "
        "to medium-risk areas."
    )

    # -----------------------------------------------------
    # TOP PRIORITY ZONES
    # -----------------------------------------------------

    st.markdown(
        "### 🚨 Top Priority Locations"
    )

    priority_zones = (

        df

        .sort_values(
            "risk_score",
            ascending=False
        )

        .head(5)

        .copy()

    )

    priority_zones["Recommended Solution"] = (

        priority_zones["risk_score"]

        .apply(

            lambda x:

                "Immediate cooling + shade + trees"

                if x >= 75

                else

                "Shade + trees + monitoring"

                if x >= 50

                else

                "Monitoring + maintain greenery"

        )

    )

    st.dataframe(

        priority_zones[

            [

                "tile_id",

                "average_temperature",

                "risk_score",

                "risk_level",

                "Recommended Solution"

            ]

        ],

        use_container_width=True,

        hide_index=True

    )


# =========================================================
# DATA & EXPORT
# =========================================================

elif page == "Data & Export":

    st.markdown(
        '<div class="section-title">'
        '📋 Data & Export'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Explore the processed heat data and download your results.'
        '</div>',
        unsafe_allow_html=True
    )

    # -----------------------------------------------------
    # FILTERS
    # -----------------------------------------------------

    st.markdown(
        "### 🔎 Data Filters"
    )

    f1, f2 = st.columns(2)

    with f1:

        selected_risk = st.multiselect(

            "Risk Level",

            [
                "HIGH",
                "MEDIUM",
                "LOW"
            ],

            default=[
                "HIGH",
                "MEDIUM",
                "LOW"
            ]

        )

    with f2:

        temp_range = st.slider(

            "Temperature Range (°C)",

            float(
                df[
                    "average_temperature"
                ].min()
            ),

            float(
                df[
                    "average_temperature"
                ].max()
            ),

            (

                float(
                    df[
                        "average_temperature"
                    ].min()
                ),

                float(
                    df[
                        "average_temperature"
                    ].max()
                )

            )

        )

    filtered = df[

        (df["risk_level"].isin(
            selected_risk
        ))

        &

        (
            df["average_temperature"]
            .between(
                temp_range[0],
                temp_range[1]
            )
        )

    ]

    st.write(
        f"Showing **{len(filtered):,}** "
        f"of **{len(df):,}** zones"
    )

    st.dataframe(

        filtered,

        use_container_width=True,

        hide_index=True

    )

    # -----------------------------------------------------
    # STATISTICS
    # -----------------------------------------------------

    st.markdown(
        "### 📊 Temperature Statistics"
    )

    stats = pd.DataFrame({

        "Metric": [

            "Minimum Temperature",

            "Maximum Temperature",

            "Average Temperature",

            "Standard Deviation",

            "Total Heat Zones",

            "High Risk Zones",

            "Medium Risk Zones",

            "Low Risk Zones"

        ],

        "Value": [

            f"{minimum_temp:.2f} °C",

            f"{maximum_temp:.2f} °C",

            f"{average_temp:.2f} °C",

            f"{df['average_temperature'].std():.2f} °C",

            f"{total_zones:,}",

            f"{high_risk:,}",

            f"{medium_risk:,}",

            f"{low_risk:,}"

        ]

    })

    st.table(stats)

    # -----------------------------------------------------
    # DOWNLOAD
    # -----------------------------------------------------

    st.markdown(
        "### ⬇️ Export Results"
    )

    csv = filtered.to_csv(
        index=False
    )

    st.download_button(

        label="📥 Download Heat Risk CSV",

        data=csv,

        file_name=
            "urban_heatguard_results.csv",

        mime="text/csv",

        use_container_width=True

    )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">

    <b>🌡️ Urban HeatGuard</b><br>

    AI-Powered Urban Heat Intelligence Platform<br><br>

    Built with Streamlit + Plotly + FortyGuard Intelligence

    </div>
    """,
    unsafe_allow_html=True
)
