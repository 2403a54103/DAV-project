import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime

# ==========================================
# PAGE SETTINGS
# ==========================================
st.set_page_config(page_title="Dynamic Environmental Monitoring", layout="wide")

st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: #e6f2ff !important;
    }
    [data-testid="stHeader"] { display: none; }
    .block-container { padding: 1rem 2rem !important; }
    [data-testid="stSidebar"] { background-color: #f2f6fa !important; }
    </style>
""", unsafe_allow_html=True)

st.title("🌍 Dynamic Environmental Monitoring Dashboard")
st.write("Simulated environmental conditions using selected year data.")

# ==========================================
# REGIONS & METRICS
# ==========================================
REGIONS = ["North", "South", "East", "West"]
METRICS = ["Air_Quality_PM25", "Soil_Moisture", "Pollution_Index"]

# ==========================================
# FUNCTION — GENERATE SIMULATED DATA
# ==========================================
def generate_dynamic_data(year, days=365):
    """Simulate environmental data for chosen year."""
    start_date = datetime(year, 1, 1)
    dates = pd.date_range(start=start_date, periods=days, freq='D')

    data = []
    for region in REGIONS:
        air_quality = np.clip(np.random.normal(50, 10, days).cumsum()/5, 10, 150)
        soil_moisture = np.clip(np.random.normal(30, 5, days).cumsum()/3, 10, 80)
        pollution_index = np.clip(np.random.normal(40, 8, days).cumsum()/4, 5, 120)

        for t, date in enumerate(dates):
            data.append({
                "Date": date,
                "Region": region,
                "Air_Quality_PM25": air_quality[t],
                "Soil_Moisture": soil_moisture[t],
                "Pollution_Index": pollution_index[t]
            })

    return pd.DataFrame(data)

# ==========================================
# SIDEBAR CONTROLS
# ==========================================
st.sidebar.header("⚙️ Dashboard Controls")

# YEAR SELECTION (PAST, PRESENT, FUTURE)
current_year = datetime.today().year
year_options = [
    current_year - 2,
    current_year - 1,
    current_year,
    current_year + 1,
    current_year + 2
]
year_sel = st.sidebar.selectbox("Select Year", year_options)

# Generate dataset for selected year
df = generate_dynamic_data(year_sel)

# DATE RANGE SELECTION
min_date = df["Date"].min()
max_date = df["Date"].max()

date_range_sel = st.sidebar.date_input(
    "Select Date Range",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# REGION SELECTION
region_sel = st.sidebar.selectbox("Select Region", ["All"] + sorted(df["Region"].unique()))

# METRICS SELECTION
metrics_sel = st.sidebar.multiselect("Select Metrics", METRICS, default=METRICS)

# CHART TYPE
chart_type = st.sidebar.selectbox("Chart Type", ["Line", "Area", "Bar", "Heatmap"])

# ==========================================
# APPLY FILTERS
# ==========================================
start_date, end_date = date_range_sel

df_filtered = df[(df["Date"] >= pd.to_datetime(start_date)) &
                 (df["Date"] <= pd.to_datetime(end_date))]

if region_sel != "All":
    df_filtered = df_filtered[df_filtered["Region"] == region_sel]

# ==========================================
# METRIC CARDS
# ==========================================
col1, col2, col3 = st.columns(3)
col1.metric("Avg PM2.5", f"{df_filtered['Air_Quality_PM25'].mean():.2f} µg/m³")
col2.metric("Avg Soil Moisture", f"{df_filtered['Soil_Moisture'].mean():.2f}%")
col3.metric("Avg Pollution Index", f"{df_filtered['Pollution_Index'].mean():.2f}")

# ==========================================
# VISUALIZATIONS
# ==========================================
for metric in metrics_sel:
    st.markdown(f"### 📊 {chart_type} Chart — {metric}")

    fig = None
    df_pivot = df_filtered.pivot(index="Date", columns="Region", values=metric)

    if chart_type == "Line":
        fig = px.line(df_filtered, x="Date", y=metric, color="Region", markers=True)

    elif chart_type == "Area":
        fig = px.area(df_filtered, x="Date", y=metric, color="Region")

    elif chart_type == "Bar":
        fig = px.bar(df_filtered, x="Date", y=metric, color="Region", barmode="group")

    elif chart_type == "Heatmap":
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.heatmap(df_pivot.T, cmap="coolwarm", annot=False, ax=ax)
        st.pyplot(fig)
        fig = None

    if fig:
        st.plotly_chart(fig, use_container_width=True)

# ==========================================
# INSIGHTS
# ==========================================
st.markdown("### 🔍 Insights")

insights = []

if df_filtered["Air_Quality_PM25"].mean() > 80:
    insights.append("🌫️ Air pollution is high in the selected period.")
else:
    insights.append("🌤️ Air quality is moderate/good.")

if df_filtered["Soil_Moisture"].mean() < 25:
    insights.append("💧 Soil moisture is low — irrigation recommended.")
else:
    insights.append("🌱 Soil moisture is stable and healthy.")

if df_filtered["Pollution_Index"].mean() > 70:
    insights.append("⚠️ Pollution levels are high — environmental risk detected.")
else:
    insights.append("✅ Pollution levels are within a safe range.")

st.markdown(
    f"<div style='background:#DCEEFB;padding:12px;border-radius:10px;'>{'<br>'.join(insights)}</div>",
    unsafe_allow_html=True
)
