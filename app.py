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
    layout="wide"
)

# =========================================================
# LOAD FORTYGUARD RESULT
# =========================================================

@st.cache_data
def load_heatmap_data():

    with open(JSON_FILE, "r", encoding="utf-8") as file:
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

        # Calculate polygon center
        longitude = np.mean(
            [point[0] for point in coordinates]
        )

        latitude = np.mean(
            [point[1] for point in coordinates]
        )

        rows.append({
            "tile_id": properties["tile_id"],
            "latitude": latitude,
            "longitude": longitude,
            "average_temperature": properties["average_temperature"],
            "min_temperature": properties["min_temperature"],
            "max_temperature": properties["max_temperature"]
        })

    return pd.DataFrame(rows)


# =========================================================
# CALCULATE HEAT RISK
# =========================================================

def calculate_risk(df):

    min_temp = df["average_temperature"].min()
    max_temp = df["average_temperature"].max()

    if max_temp == min_temp:

        df["risk_score"] = 0

    else:

        df["risk_score"] = (
            (
                df["average_temperature"] - min_temp
            )
            /
            (
                max_temp - min_temp
            )
        ) * 100

    def risk_level(score):

        if score >= 75:
            return "HIGH"

        elif score >= 50:
            return "MEDIUM"

        else:
            return "LOW"

    df["risk_level"] = df["risk_score"].apply(risk_level)

    return df


# =========================================================
# HEADER
# =========================================================

st.title("🌡️ Urban HeatGuard")

st.subheader(
    "AI-Powered Urban Heat Risk Detection"
)

st.write(
    """
    Urban HeatGuard uses FortyGuard temperature intelligence
    to identify urban heat hotspots and prioritize areas
    requiring cooling interventions.
    """
)

st.info(
    f"FortyGuard Activity ID: {ACTIVITY_ID}"
)


# =========================================================
# LOAD DATA
# =========================================================

try:

    with st.spinner("Loading FortyGuard heatmap..."):

        df = load_heatmap_data()

except FileNotFoundError:

    st.error(
        "fortyguard_result.json was not found. "
        "Make sure it is in the same folder as app.py."
    )

    st.stop()

except Exception as e:

    st.error(
        f"Error loading FortyGuard data: {e}"
    )

    st.stop()


# =========================================================
# CALCULATE RISK
# =========================================================

df = calculate_risk(df)


# =========================================================
# METRICS
# =========================================================

average_temp = df["average_temperature"].mean()

minimum_temp = df["average_temperature"].min()

maximum_temp = df["average_temperature"].max()

high_risk = len(
    df[df["risk_level"] == "HIGH"]
)

medium_risk = len(
    df[df["risk_level"] == "MEDIUM"]
)

low_risk = len(
    df[df["risk_level"] == "LOW"]
)


col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "🌡️ Average Temperature",
    f"{average_temp:.2f} °C"
)

col2.metric(
    "❄️ Minimum Temperature",
    f"{minimum_temp:.2f} °C"
)

col3.metric(
    "🔥 Maximum Temperature",
    f"{maximum_temp:.2f} °C"
)

col4.metric(
    "🚨 High Risk Zones",
    high_risk
)


# =========================================================
# HEAT RISK ANALYSIS
# =========================================================

st.header("🚨 Heat Risk Analysis")

risk_col1, risk_col2, risk_col3 = st.columns(3)

risk_col1.metric(
    "HIGH Risk",
    high_risk
)

risk_col2.metric(
    "MEDIUM Risk",
    medium_risk
)

risk_col3.metric(
    "LOW Risk",
    low_risk
)


if high_risk > 0:

    st.warning(
        f"⚠️ {high_risk} high-risk heat zone(s) "
        "have been identified."
    )

else:

    st.success(
        "✅ No high-risk heat zones were identified."
    )


# =========================================================
# TEMPERATURE MAP
# =========================================================

st.header("🗺️ Urban Temperature Map")

fig = px.scatter_mapbox(
    df,
    lat="latitude",
    lon="longitude",
    color="average_temperature",
    size="average_temperature",
    hover_name="tile_id",

    hover_data={
        "average_temperature": ":.2f",
        "min_temperature": ":.2f",
        "max_temperature": ":.2f",
        "latitude": ":.5f",
        "longitude": ":.5f"
    },

    color_continuous_scale="Turbo",

    zoom=14,

    height=650
)

fig.update_layout(

    mapbox_style="open-street-map",

    margin={
        "r": 0,
        "t": 0,
        "l": 0,
        "b": 0
    }
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# =========================================================
# RISK MAP
# =========================================================

st.header("🔥 Heat Risk Map")

risk_fig = px.scatter_mapbox(

    df,

    lat="latitude",

    lon="longitude",

    color="risk_score",

    size="risk_score",

    hover_name="tile_id",

    hover_data={

        "average_temperature": ":.2f",

        "min_temperature": ":.2f",

        "max_temperature": ":.2f",

        "risk_score": ":.1f",

        "risk_level": True

    },

    color_continuous_scale="RdYlGn_r",

    range_color=[0, 100],

    zoom=14,

    height=650

)

risk_fig.update_layout(

    mapbox_style="open-street-map",

    margin={
        "r": 0,
        "t": 0,
        "l": 0,
        "b": 0
    }

)

st.plotly_chart(
    risk_fig,
    use_container_width=True
)


# =========================================================
# TOP HOTSPOTS
# =========================================================

st.header("🔥 Highest Risk Areas")

hotspots = (

    df
    .sort_values(
        "risk_score",
        ascending=False
    )
    .head(10)

)

st.dataframe(

    hotspots[
        [
            "tile_id",
            "latitude",
            "longitude",
            "average_temperature",
            "min_temperature",
            "max_temperature",
            "risk_score",
            "risk_level"
        ]
    ],

    use_container_width=True

)


# =========================================================
# TEMPERATURE DISTRIBUTION
# =========================================================

st.header("📊 Temperature Distribution")

hist_fig = px.histogram(

    df,

    x="average_temperature",

    nbins=20,

    title="Urban Temperature Distribution",

    labels={
        "average_temperature":
        "Temperature (°C)"
    }

)

st.plotly_chart(

    hist_fig,

    use_container_width=True

)


# =========================================================
# RISK DISTRIBUTION
# =========================================================

st.header("📈 Risk Zone Distribution")

risk_counts = (

    df["risk_level"]
    .value_counts()
    .reset_index()

)

risk_counts.columns = [
    "Risk Level",
    "Number of Zones"
]

pie_fig = px.pie(

    risk_counts,

    names="Risk Level",

    values="Number of Zones",

    title="Heat Risk Zones"

)

st.plotly_chart(

    pie_fig,

    use_container_width=True

)


# =========================================================
# RECOMMENDATIONS
# =========================================================

st.header("💡 Recommended Actions")

st.write(
    "Urban HeatGuard converts detected heat-risk zones into "
    "practical cooling actions for city planners."
)

# ---------------------------------------------------------
# OVERALL PRIORITY
# ---------------------------------------------------------

if high_risk >= 20:

    st.error(
        f"""
        🔴 CRITICAL PRIORITY

        {high_risk} high-risk zones require immediate attention.

        Recommended actions:
        • 🌳 Increase tree coverage in high-risk zones
        • 🏠 Install shade structures in exposed public areas
        • 💧 Establish cooling and hydration stations
        • 🛣️ Use reflective/cool materials on roads and rooftops
        • 🏙️ Prioritize these zones for urban cooling investment
        """
    )

elif high_risk > 0:

    st.warning(
        f"""
        🟠 HIGH PRIORITY

        {high_risk} high-risk zones have been detected.

        Recommended actions:
        • 🌳 Increase vegetation and tree coverage
        • 🏠 Add shaded pedestrian and waiting areas
        • 💧 Consider cooling/hydration stations
        • 🌿 Improve green infrastructure
        • 📡 Continue monitoring these locations
        """
    )

else:

    st.success(
        """
        🟢 LOW PRIORITY

        No high-risk zones were detected.

        Recommended actions:
        • 🌳 Maintain existing green infrastructure
        • 📡 Continue monitoring temperature patterns
        • 🏙️ Protect existing shaded areas
        """
    )


# ---------------------------------------------------------
# ZONE-SPECIFIC RECOMMENDATIONS
# ---------------------------------------------------------

st.subheader("🎯 Zone-Specific Action Plan")

if high_risk > 0:

    st.markdown(
        f"""
        ### 🔴 High-Risk Zones — {high_risk}

        **Action:** Immediate intervention recommended.

        - 🌳 Plant trees and increase vegetation
        - 🏠 Install permanent shade structures
        - 💧 Add cooling/hydration stations
        - 🛣️ Consider cool roofs and reflective surfaces
        - 🚨 Prioritize emergency heat-response resources
        """
    )


if medium_risk > 0:

    st.markdown(
        f"""
        ### 🟠 Medium-Risk Zones — {medium_risk}

        **Action:** Prevent these areas from becoming severe hotspots.

        - 🌿 Increase urban greenery
        - 🏠 Add temporary or permanent shade
        - 🚶 Improve shaded pedestrian pathways
        - 📡 Monitor temperature changes
        - 🌳 Prioritize future tree planting
        """
    )


if low_risk > 0:

    st.markdown(
        f"""
        ### 🟢 Low-Risk Zones — {low_risk}

        **Action:** Continue monitoring and maintain current conditions.

        - 🌳 Protect existing vegetation
        - 📡 Continue temperature monitoring
        - 🏙️ Maintain existing cooling infrastructure
        """
    )


# ---------------------------------------------------------
# TOP 5 PRIORITY ZONES
# ---------------------------------------------------------

st.subheader("🚨 Top 5 Priority Intervention Zones")

priority_zones = (
    df
    .sort_values("risk_score", ascending=False)
    .head(5)
    .copy()
)

priority_zones["Recommended Action"] = priority_zones[
    "risk_score"
].apply(
    lambda x:
        "Immediate cooling + shade + vegetation"
        if x >= 75
        else
        "Shade + vegetation + monitoring"
        if x >= 50
        else
        "Monitoring + maintain green infrastructure"
)

st.dataframe(
    priority_zones[
        [
            "tile_id",
            "latitude",
            "longitude",
            "average_temperature",
            "risk_score",
            "risk_level",
            "Recommended Action"
        ]
    ],
    use_container_width=True
)


# ---------------------------------------------------------
# RESOURCE PRIORITIZATION
# ---------------------------------------------------------

st.subheader("🏗️ Resource Prioritization")

resource_col1, resource_col2, resource_col3 = st.columns(3)

resource_col1.metric(
    "🌳 Green Infrastructure",
    f"{high_risk} zones"
)

resource_col2.metric(
    "💧 Cooling Stations",
    f"{high_risk} zones"
)

resource_col3.metric(
    "🏠 Shade Structures",
    f"{high_risk + medium_risk} zones"
)


st.info(
    """
    💡 Strategy:
    
    Resources should be prioritized in the highest-risk
    locations instead of applying the same intervention
    across the entire city.
    """
)


# =========================================================
# DATA SUMMARY
# =========================================================

st.header("📋 Temperature Statistics")

stats = pd.DataFrame({

    "Metric": [
        "Minimum Temperature",
        "Maximum Temperature",
        "Average Temperature",
        "Standard Deviation",
        "Total Heat Zones"
    ],

    "Value": [
        f"{minimum_temp:.4f} °C",
        f"{maximum_temp:.4f} °C",
        f"{average_temp:.4f} °C",
        f"{df['average_temperature'].std():.4f} °C",
        len(df)
    ]

})

st.table(stats)


# =========================================================
# DOWNLOAD DATA
# =========================================================

st.header("⬇️ Download Results")

csv = df.to_csv(index=False)

st.download_button(

    label="Download Heat Risk CSV",

    data=csv,

    file_name="urban_heatguard_results.csv",

    mime="text/csv"

)


# =========================================================
# PROJECT INFORMATION
# =========================================================

st.header("🎯 About Urban HeatGuard")

st.write(
    """
    Urban HeatGuard is an AI-powered urban heat
    intelligence system.

    The system analyzes FortyGuard temperature data,
    calculates relative heat-risk scores, identifies
    spatial hotspots, visualizes temperature patterns,
    and recommends areas where cooling interventions
    should be prioritized.
    """
)

st.caption(
    f"FortyGuard Activity ID: {ACTIVITY_ID}"
)