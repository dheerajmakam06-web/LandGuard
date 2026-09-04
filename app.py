from __future__ import annotations

import time
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from risk_engine import score_dataframe
from sample_data import find_nearest_safe_place, generate_sensor_data

st.set_page_config(page_title="LandGuard | NER Early Warning", page_icon="⛰️", layout="wide")

st.markdown("""
<style>
:root { --ink:#17231c; --muted:#617168; --paper:#f5f7f1; --line:#dce5dc; }
.stApp { background:radial-gradient(circle at 92% 8%, rgba(213,166,66,.23), transparent 26rem), radial-gradient(circle at 4% 72%, rgba(40,96,74,.16), transparent 30rem), linear-gradient(135deg,#f8faf4 0%,#edf4eb 52%,#fff8e8 100%); color:var(--ink); }
[data-testid="stSidebar"] { background:linear-gradient(180deg,#123b2c 0%,#1e5a43 56%,#133526 100%); }
[data-testid="stSidebar"] * { color:#eff8ef !important; }
.block-container { max-width: 1380px; padding-top: 2rem; padding-bottom:3rem; }
.hero { background:linear-gradient(120deg,#102f24 0%,#246047 54%,#b88728 145%); color:white; padding:2.3rem 2.5rem; border-radius:18px; margin-bottom:1.4rem; box-shadow:0 14px 34px rgba(23,58,43,.18); border:1px solid rgba(255,255,255,.2); }
.hero h1 { font-family: Georgia, serif; font-size:2.8rem; letter-spacing:.02em; margin:0 0 .4rem; }
.hero p { color:#dcebdc; max-width:760px; margin:0; }
.metric { background:rgba(255,255,255,.88); border:1px solid rgba(220,229,220,.95); border-top:4px solid #28604a; border-radius:12px; padding:1rem 1.15rem; box-shadow:0 8px 22px rgba(23,58,43,.08); min-height:96px; }
.metric small { color:var(--muted); text-transform:uppercase; letter-spacing:.08em; font-weight:700; }
.metric strong { display:block; font-size:1.8rem; margin-top:.25rem; }
.alert { padding:.9rem 1rem; border-left:5px solid; background:rgba(255,255,255,.92); border-radius:9px; margin:.5rem 0; box-shadow:0 5px 16px rgba(23,58,43,.07); }
.warning-table { background:rgba(255,255,255,.82); border:1px solid var(--line); border-radius:12px; padding:1rem 1.15rem; box-shadow:0 8px 22px rgba(23,58,43,.06); }
.legend { background:rgba(255,255,255,.9); border:1px solid var(--line); border-radius:10px; padding:.85rem 1rem; margin-top:1rem; box-shadow:0 6px 18px rgba(23,58,43,.06); }
.legend-row { display:flex; align-items:center; gap:.5rem; margin:.35rem 0; }
.dot { width:12px; height:12px; border-radius:50%; display:inline-block; }
h2, h3 { color:#1d4936; }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=1)
def load_data() -> pd.DataFrame:
    return score_dataframe(generate_sensor_data())

with st.sidebar:
    st.markdown("## ⛰️ LandGuard")
    st.caption("AI-assisted landslide early warning for Northeast India")
    page = st.radio("Workspace", ["Overview", "Live Monitoring", "Risk Assessment", "Alerts & Response", "Project Notes & Graphs"])
    st.divider()
    auto_refresh = st.toggle("Auto-refresh demo", value=False)
    selected_state = st.selectbox("Focus state", ["All states", "Sikkim", "Arunachal Pradesh", "Assam", "Meghalaya", "Nagaland", "Mizoram", "Manipur", "Tripura"])

if auto_refresh:
    time.sleep(1)
    st.rerun()

data = load_data()
latest = data.sort_values("timestamp").groupby("district", as_index=False).tail(1).copy()
view = latest if selected_state == "All states" else latest[latest["state"] == selected_state]
critical = int((latest["risk_level"] == "CRITICAL").sum())
high = int((latest["risk_level"] == "HIGH").sum())
latest_timestamp = latest["timestamp"].max()
current_time = datetime.now()

# Compare each node with its recent baseline so rising risk is visible before it reaches HIGH.
recent = data[data["timestamp"] >= latest_timestamp - pd.Timedelta(hours=6)]
baseline = recent.groupby("district")["risk_score"].mean().rename("six_hour_average")
early_warning = latest.join(baseline, on="district")
early_warning["trend"] = (early_warning["risk_score"] - early_warning["six_hour_average"]).round(1)
early_warning["early_warning"] = early_warning.apply(
    lambda row: "RISING" if row["trend"] >= 3 else "STABLE", axis=1
)


def risk_level_for_score(score: float) -> str:
    if score >= 75:
        return "CRITICAL"
    if score >= 50:
        return "HIGH"
    if score >= 25:
        return "MODERATE"
    return "LOW"


# Conservative one-hour projection for the academic demo; production use needs a trained time-series model.
early_warning["predicted_score_1h"] = (early_warning["risk_score"] + early_warning["trend"].clip(lower=0) * 0.5).clip(upper=100).round(1)
early_warning["predicted_level_1h"] = early_warning["predicted_score_1h"].map(risk_level_for_score)
selected_nodes = set(view["district"])
priority_alerts = early_warning[
    early_warning["district"].isin(selected_nodes)
    & early_warning["risk_level"].isin(["HIGH", "CRITICAL"])
].sort_values("risk_score", ascending=False)
predicted_alerts = early_warning[
    early_warning["district"].isin(selected_nodes)
    & early_warning["predicted_level_1h"].isin(["HIGH", "CRITICAL"])
    & ~early_warning["risk_level"].isin(["HIGH", "CRITICAL"])
].sort_values("predicted_score_1h", ascending=False)
moderate_alerts = early_warning[
    early_warning["district"].isin(selected_nodes)
    & (early_warning["risk_level"] == "MODERATE")
].sort_values("risk_score", ascending=False)

st.markdown("<div class='hero'><h1>LandGuard</h1><p>AI-based early warning and landslide risk monitoring across the North Eastern Region of India.</p></div>", unsafe_allow_html=True)

if not priority_alerts.empty:
    st.error(f"IMMEDIATE SAFETY ALERT: {len(priority_alerts)} location(s) require urgent response. Move people away from unstable slopes and follow local authority instructions.")
    for _, alert in priority_alerts.iterrows():
        safe_place = find_nearest_safe_place(alert["latitude"], alert["longitude"])
        st.markdown(
            f"**{alert['risk_level']} · {alert['district']}, {alert['state']} · score {alert['risk_score']}**  "
            f"\nNearest suggested evacuation point: **{safe_place['name']}**, {safe_place['distance_km']} km away ({safe_place['address']})."
        )
elif not moderate_alerts.empty:
    locations = ", ".join(f"{row.district} ({row.risk_score})" for row in moderate_alerts.itertuples())
    st.warning(f"ADVANCE WARNING: Moderate-risk locations to monitor closely: {locations}. Prepare transport and move vulnerable people early if conditions worsen.")

if not predicted_alerts.empty:
    st.warning(f"PREDICTED NEXT-HOUR DANGER: {len(predicted_alerts)} location(s) may reach High/Critical risk. Start moving vulnerable people away from slopes now.")
    for _, alert in predicted_alerts.iterrows():
        safe_place = find_nearest_safe_place(alert["latitude"], alert["longitude"])
        st.markdown(
            f"**Predicted {alert['predicted_level_1h']} · {alert['district']}, {alert['state']}** "
            f"(current {alert['risk_score']}, projected {alert['predicted_score_1h']} in 1 hour)  \n"
            f"Move from the danger area to **{safe_place['name']}**, approximately **{safe_place['distance_km']} km** away ({safe_place['address']}). Follow police and disaster-management instructions and use official routes."
        )

if page == "Overview":
    scope_label = "All NER states" if selected_state == "All states" else selected_state
    critical = int((view["risk_level"] == "CRITICAL").sum())
    high = int((view["risk_level"] == "HIGH").sum())
    st.subheader(f"Regional situation room · {scope_label}")
    cols = st.columns(4)
    metrics = [("Monitored locations", len(view), "district nodes in scope"), ("Critical alerts", critical, "immediate action"), ("High-risk alerts", high, "watch closely"), ("Current time", current_time.strftime("%H:%M:%S"), "local time")]
    for col, (label, value, note) in zip(cols, metrics):
        col.markdown(f"<div class='metric'><small>{label}</small><strong>{value}</strong><span>{note}</span></div>", unsafe_allow_html=True)
    st.caption(f"Live clock: {current_time.strftime('%A, %d %B %Y at %H:%M:%S')} local time. Sensor data last updated: {latest_timestamp.strftime('%d %B %Y at %H:%M')}.")
    st.markdown("### Advance warning locations")
    warning_locations = early_warning[
        early_warning["district"].isin(view["district"])
        & early_warning["risk_level"].isin(["MODERATE", "HIGH", "CRITICAL"])
    ].copy()
    warning_locations = warning_locations.sort_values(["risk_score", "trend"], ascending=False)
    if warning_locations.empty:
        st.success("No Moderate, High, or Critical locations in the selected region.")
    else:
        warning_locations = warning_locations[["state", "district", "risk_level", "risk_score", "trend", "early_warning", "risk_reason"]]
        st.dataframe(
            warning_locations,
            use_container_width=True,
            hide_index=True,
            column_config={
                "risk_level": st.column_config.TextColumn("Current risk"),
                "risk_score": st.column_config.ProgressColumn("Score", min_value=0, max_value=100, format="%f"),
                "trend": st.column_config.NumberColumn("6-hour change", format="%+.1f"),
                "early_warning": st.column_config.TextColumn("Advance signal"),
                "risk_reason": st.column_config.TextColumn("Why"),
            },
        )
        st.caption("RISING means the current score is at least 3 points above the node's recent six-hour average. Treat Moderate locations as early-warning areas and High/Critical locations as danger areas.")
    st.write("")
    left, right = st.columns([1.15, .85])
    with left:
        st.markdown("### Risk by district")
        chart = px.bar(view.sort_values("risk_score"), x="risk_score", y="district", color="risk_level", orientation="h", color_discrete_map={"LOW":"#15803d","MODERATE":"#ca8a04","HIGH":"#ea580c","CRITICAL":"#dc2626"}, labels={"risk_score":"Risk score (0-100)", "district":""})
        chart.update_layout(height=420, margin=dict(l=0,r=0,t=10,b=0), showlegend=False)
        st.plotly_chart(chart, use_container_width=True)
    with right:
        st.markdown("### NER monitoring map")
        map_data = view.rename(columns={"latitude":"lat", "longitude":"lon"})[["lat", "lon", "risk_color"]]
        st.map(map_data, latitude="lat", longitude="lon", color="risk_color", size=180)
        st.markdown("""
        <div class="legend">
        <b>Map colour guide</b>
        <div class="legend-row"><span class="dot" style="background:#15803d"></span><b>Green · Safe</b> Low risk; normal monitoring.</div>
        <div class="legend-row"><span class="dot" style="background:#ca8a04"></span><b>Yellow · Warning</b> Moderate risk; prepare and monitor.</div>
        <div class="legend-row"><span class="dot" style="background:#ea580c"></span><b>Orange · Danger</b> High risk; begin response planning.</div>
        <div class="legend-row"><span class="dot" style="background:#dc2626"></span><b>Red · Emergency</b> Critical risk; move people to safety.</div>
        </div>
        """, unsafe_allow_html=True)
        st.caption("Demo node locations. Replace with field gateway GPS coordinates for deployment.")
    st.markdown("### Area safety status")
    area_status = view[["state", "district", "risk_score", "risk_level"]].sort_values("risk_score", ascending=False).copy()
    area_status["area_status"] = area_status["risk_level"].map({"LOW":"SAFE", "MODERATE":"WARNING", "HIGH":"DANGER", "CRITICAL":"EMERGENCY"})
    st.dataframe(
        area_status[["state", "district", "area_status", "risk_level", "risk_score"]],
        use_container_width=True,
        hide_index=True,
        column_config={"risk_score": st.column_config.ProgressColumn("Risk score", min_value=0, max_value=100, format="%f")},
    )

elif page == "Live Monitoring":
    st.subheader("Sensor telemetry")
    st.info(f"Dashboard time: {datetime.now().strftime('%d %B %Y, %H:%M:%S')} · Last sensor update: {latest_timestamp.strftime('%d %B %Y, %H:%M')}")
    district = st.selectbox("Select monitoring node", sorted(view["district"].unique()))
    history = data[data["district"] == district].sort_values("timestamp").tail(48)
    a, b = st.columns(2)
    with a:
        fig = px.line(history, x="timestamp", y=["rainfall_24h_mm", "soil_moisture_pct"], labels={"value":"Reading", "timestamp":""}, title="Rainfall and soil moisture")
        fig.update_layout(legend_title_text="", height=340)
        st.plotly_chart(fig, use_container_width=True)
    with b:
        fig = px.line(history, x="timestamp", y=["displacement_mm", "risk_score"], labels={"value":"Reading", "timestamp":""}, title="Ground movement and risk score")
        fig.update_layout(legend_title_text="", height=340)
        st.plotly_chart(fig, use_container_width=True)
    st.dataframe(history.tail(12).sort_values("timestamp", ascending=False), use_container_width=True, hide_index=True)

elif page == "Risk Assessment":
    st.subheader("Explainable AI risk assessment")
    st.info("The demonstration model combines rainfall, soil moisture, slope, displacement, and micro-seismic activity. In a production study, calibrate thresholds with historical landslide records and domain experts.")
    table = view[["state", "district", "risk_score", "risk_level", "risk_reason", "rainfall_24h_mm", "soil_moisture_pct", "slope_deg", "displacement_mm"]].sort_values("risk_score", ascending=False)
    st.dataframe(table, use_container_width=True, hide_index=True, column_config={"risk_score": st.column_config.ProgressColumn("Risk score", min_value=0, max_value=100, format="%f")})
    selected = st.selectbox("Inspect node explanation", view["district"].tolist())
    row = view[view["district"] == selected].iloc[0]
    result = row["risk_reason"].split("; ")
    st.markdown(f"### {selected}: {row['risk_level']} ({row['risk_score']}/100)")
    for reason in result:
        st.markdown(f"- {reason}")
    radar = go.Figure(go.Scatterpolar(r=[row["rainfall_24h_mm"] / 180 * 100, row["soil_moisture_pct"], row["slope_deg"] / 45 * 100, row["displacement_mm"] / 30 * 100, row["seismic_activity"] / .8 * 100], theta=["Rainfall", "Moisture", "Slope", "Displacement", "Seismic"], fill="toself"))
    radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0,100])), height=380, margin=dict(l=30,r=30,t=30,b=30))
    st.plotly_chart(radar, use_container_width=True)

elif page == "Alerts & Response":
    st.subheader("Prioritized response queue")
    alerts = view[view["risk_level"].isin(["CRITICAL", "HIGH"])].sort_values("risk_score", ascending=False)
    if alerts.empty:
        st.success("No high-priority alerts in the selected area.")
    for _, alert in alerts.iterrows():
        action = "Evacuate vulnerable households; contact district disaster management authority." if alert["risk_level"] == "CRITICAL" else "Increase patrol frequency; prepare evacuation and road-closure teams."
        st.markdown(f"<div class='alert' style='border-color:{alert['risk_color']}'><b>{alert['risk_level']} · {alert['district']}, {alert['state']} · score {alert['risk_score']}</b><br>{alert['risk_reason']}<br><span>Recommended action: {action}</span></div>", unsafe_allow_html=True)
    st.download_button("Download alert queue (CSV)", alerts.to_csv(index=False), "landguard_alerts.csv", "text/csv")

else:
    st.subheader("College project blueprint")
    st.markdown("""
**Problem:** Landslides in the NER are triggered by intense rainfall, saturated soil, steep slopes, road cutting, and seismic conditions. Communities need localized warnings before a failure occurs.

**Proposed system:** IoT sensor nodes send readings to an API. The processing layer validates readings, computes an explainable risk score, stores time-series data, and sends alerts to a dashboard, SMS gateway, or district control room.

**Suggested phases:**
1. Demonstration: use this simulated data and dashboard.
2. Prototype: connect ESP32/LoRa sensors for rain, soil moisture, tilt, and vibration.
3. Validation: compare scores with IMD rainfall and historical landslide inventories.
4. Deployment study: add authentication, PostgreSQL/TimescaleDB, Docker, SMS, offline buffering, and model monitoring.

**Important:** This is a decision-support prototype, not an official emergency warning system. Real deployment requires calibrated thresholds, field testing, redundant sensors, and approval from the responsible authorities.
""")
    st.markdown("### System design")
    st.markdown("""
    <div class="warning-table">
    <b>1. Field sensor layer</b><br>
    Rain gauge, soil-moisture sensor, tilt/displacement sensor, vibration sensor, GPS, and ESP32/LoRa gateway.<br><br>
    <b>2. Communication layer</b><br>
    LoRa, Wi-Fi, or 4G sends readings to the monitoring server. Offline readings should be buffered until the connection returns.<br><br>
    <b>3. Intelligence layer</b><br>
    Cleans sensor readings, combines rainfall, moisture, slope, displacement, and seismic indicators, then produces an explainable risk score.<br><br>
    <b>4. Decision and alert layer</b><br>
    Classifies areas as Safe, Warning, Danger, or Emergency and sends dashboard, SMS, or control-room alerts.<br><br>
    <b>5. User layer</b><br>
    District officers and field teams view the map, affected area, nearest verified shelter, trend, and recommended response.
    </div>
    """, unsafe_allow_html=True)
    st.markdown("### Project module design")
    module_design = pd.DataFrame([
        {"Module": "Sensor data", "Current MVP": "Simulated NER readings", "Production version": "ESP32/LoRa field nodes"},
        {"Module": "Risk engine", "Current MVP": "Explainable weighted model", "Production version": "Calibrated ML model with historical events"},
        {"Module": "Storage", "Current MVP": "In-memory pandas data", "Production version": "PostgreSQL/TimescaleDB"},
        {"Module": "Alerts", "Current MVP": "Dashboard banners", "Production version": "SMS, siren, email, and official control room"},
        {"Module": "Safe places", "Current MVP": "Demo evacuation points", "Production version": "Verified shelters and GIS route guidance"},
    ])
    st.dataframe(module_design, use_container_width=True, hide_index=True)
    st.markdown("### NER state-wise project graphs")
    state_summary = latest.groupby("state", as_index=False).agg(
        average_risk_score=("risk_score", "mean"),
        monitored_districts=("district", "count"),
        highest_risk_score=("risk_score", "max"),
    )
    state_summary["average_risk_score"] = state_summary["average_risk_score"].round(1)
    state_summary = state_summary.sort_values("average_risk_score", ascending=False)
    graph_left, graph_right = st.columns(2)
    with graph_left:
        state_graph = px.bar(
            state_summary,
            x="average_risk_score",
            y="state",
            orientation="h",
            color="average_risk_score",
            color_continuous_scale=["#15803d", "#ca8a04", "#ea580c", "#dc2626"],
            title="Average risk score by NER state",
            labels={"average_risk_score": "Average score", "state": ""},
        )
        state_graph.update_layout(height=430, coloraxis_showscale=False, margin=dict(l=0, r=0, t=45, b=0))
        st.plotly_chart(state_graph, use_container_width=True)
    with graph_right:
        level_counts = latest["risk_level"].value_counts().rename_axis("risk_level").reset_index(name="locations")
        level_graph = px.pie(
            level_counts,
            names="risk_level",
            values="locations",
            hole=.45,
            title="NER locations by risk category",
            color="risk_level",
            color_discrete_map={"LOW":"#15803d", "MODERATE":"#ca8a04", "HIGH":"#ea580c", "CRITICAL":"#dc2626"},
        )
        level_graph.update_layout(height=430, margin=dict(l=0, r=0, t=45, b=0))
        st.plotly_chart(level_graph, use_container_width=True)
    st.dataframe(state_summary, use_container_width=True, hide_index=True)
    st.download_button("Download NER state summary (CSV)", state_summary.to_csv(index=False), "landguard_ner_state_summary.csv", "text/csv")
    st.download_button("Download state risk graph (HTML)", state_graph.to_html(include_plotlyjs="cdn"), "landguard_state_risk_graph.html", "text/html")

st.caption("LandGuard MVP · Simulated data for academic demonstration · Last generated dataset: 72 hours")
