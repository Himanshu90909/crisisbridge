from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from analytics import (
    build_resource_recommendations,
    calculate_priority,
    get_filtered_requests,
    load_data,
)
from live_sources import fetch_earthquakes, fetch_reliefweb_updates, fetch_weather, geocode_location

st.set_page_config(
    page_title="CrisisBridge | Emergency Response Intelligence",
    page_icon="CB",
    layout="wide",
    initial_sidebar_state="expanded",
)

ROOT = Path(__file__).parent

# ---------- Theme ----------
st.markdown(
    """
    <style>
    :root { --ink: #102a43; --muted: #627d98; --teal: #0f766e; --orange: #ea580c; --red: #b91c1c; }
    .stApp { background: #f5f7fa; }
    .block-container { padding-top: 2rem; max-width: 1450px; }
    .brand { display:flex; align-items:center; gap:14px; margin-bottom: 8px; }
    .brand-mark { width:46px; height:46px; border-radius:14px; background:#102a43; color:#fff; display:grid; place-items:center; font-weight:800; letter-spacing:-1px; }
    .eyebrow { color:#0f766e; font-size:.76rem; font-weight:800; letter-spacing:.12em; text-transform:uppercase; }
    .hero { background:linear-gradient(110deg,#102a43 0%,#1f4e79 70%,#0f766e 100%); color:white; padding:24px 28px; border-radius:18px; margin:18px 0 24px; }
    .hero h1 { color:white; margin:0 0 8px; font-size:2.2rem; }
    .hero p { color:#d9eaf7; margin:0; max-width:850px; font-size:1rem; }
    .section-title { color:#102a43; font-size:1.25rem; font-weight:800; margin:24px 0 10px; }
    .alert { padding:14px 16px; border-left:5px solid #ea580c; background:#fff7ed; border-radius:8px; color:#7c2d12; margin:8px 0 16px; }
    [data-testid="stMetricValue"] { color:#102a43; }
    </style>
    """,
    unsafe_allow_html=True,
)

requests, shelters, hospitals, resources = load_data(ROOT / "data")
requests["priority_score"] = requests.apply(calculate_priority, axis=1)

with st.sidebar:
    st.markdown("### CrisisBridge")
    st.caption("Emergency response intelligence prototype")
    st.divider()
    selected_status = st.multiselect(
        "Request status",
        sorted(requests["status"].unique()),
        default=sorted(requests["status"].unique()),
    )
    selected_need = st.multiselect(
        "Need type",
        sorted(requests["need_type"].unique()),
        default=sorted(requests["need_type"].unique()),
    )
    selected_zone = st.multiselect(
        "Response zone",
        sorted(requests["zone"].unique()),
        default=sorted(requests["zone"].unique()),
    )
    st.divider()
    st.caption("Prototype data is synthetic and designed for demonstration.")

filtered = get_filtered_requests(requests, selected_status, selected_need, selected_zone)
critical = int((filtered["priority"] == "Critical").sum())
open_requests = int((filtered["status"] != "Completed").sum())
people_impacted = int(filtered["people_affected"].sum())
active_shelters = int((shelters["status"] == "Open").sum())

st.markdown(
    '<div class="brand"><div class="brand-mark">CB</div><div><div class="eyebrow">Response operations platform</div><strong style="font-size:1.35rem;color:#102a43">CrisisBridge</strong></div></div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="hero"><h1>Make every emergency resource count.</h1><p>A decision-support dashboard for coordinating shelters, hospitals, supplies, volunteers, and urgent citizen requests during a disaster.</p></div>',
    unsafe_allow_html=True,
)

# ---------- World Intelligence OS prototype ----------
world_tabs = st.tabs(["Global Pulse", "Problem Radar", "World Graph", "Ask the World"])
with world_tabs[0]:
    st.markdown("**What is happening in the world right now?**")
    pulse_items = [
        {"Domain": "Hazards", "Signal": "Live earthquake activity", "Coverage": "Global", "Status": "Live · USGS", "Action": "Open the live hazard map"},
        {"Domain": "Climate", "Signal": "Location weather context", "Coverage": "Country → village search", "Status": "Live · Open-Meteo", "Action": "Search any location below"},
        {"Domain": "Humanitarian", "Signal": "Situation reports", "Coverage": "Global", "Status": "Connector resilient", "Action": "Review source-linked updates"},
        {"Domain": "Response", "Signal": "Emergency requests and resources", "Coverage": "Operational zones", "Status": "Prototype workspace", "Action": "Triage and dispatch"},
    ]
    st.dataframe(pd.DataFrame(pulse_items), use_container_width=True, hide_index=True)
    st.caption("Pulse items show source status honestly: live, connector-resilient, or prototype. This avoids presenting fabricated global intelligence as fact.")

with world_tabs[1]:
    st.markdown("**Problem Radar — transparent prioritization of signals**")
    radar = pd.DataFrame([
        {"Problem": "Emergency resource shortage", "Impact": 92, "Urgency": 95, "Growth": "↑↑", "Evidence": "CrisisBridge triage data", "Mode": "Prototype"},
        {"Problem": "Earthquake activity", "Impact": 86, "Urgency": 88, "Growth": "Live", "Evidence": "USGS earthquake feed", "Mode": "Live"},
        {"Problem": "Location-level weather exposure", "Impact": 82, "Urgency": 80, "Growth": "Live", "Evidence": "Open-Meteo context", "Mode": "Live"},
        {"Problem": "Humanitarian information fragmentation", "Impact": 79, "Urgency": 84, "Growth": "↑", "Evidence": "Source integration layer", "Mode": "Architecture"},
        {"Problem": "Food, energy, markets, and health signals", "Impact": 70, "Urgency": 65, "Growth": "Planned", "Evidence": "Future API adapters", "Mode": "Roadmap"},
    ])
    radar["Radar score"] = (radar["Impact"] * 0.45 + radar["Urgency"] * 0.55).round().astype(int)
    st.dataframe(radar.sort_values("Radar score", ascending=False), use_container_width=True, hide_index=True, column_config={"Radar score": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%d")})
    selected_problem = st.selectbox("Explore a problem", radar["Problem"].tolist())
    selected_row = radar[radar["Problem"] == selected_problem].iloc[0]
    st.info(f"**{selected_problem}** — impact {selected_row['Impact']}/100, urgency {selected_row['Urgency']}/100, evidence mode: {selected_row['Mode']}. Next: connect a verified domain-specific feed before forecasting or recommending action.")

with world_tabs[2]:
    st.markdown("**AI World Graph — connect signals into explainable chains**")
    st.caption("This graph is an explainable prototype. Production relationships should be backed by dated datasets and confidence scores.")
    labels = ["India", "Low rainfall", "Crop production", "Food prices", "Inflation", "Consumer spending", "Business impact"]
    sources = [0, 1, 2, 3, 4, 5]
    targets = [1, 2, 3, 4, 5, 6]
    values = [8, 7, 6, 5, 4, 3]
    fig_graph = go.Figure(go.Sankey(node=dict(label=labels, color=["#102a43", "#0f766e", "#0f766e", "#ea580c", "#ea580c", "#d97706", "#b91c1c"]), link=dict(source=sources, target=targets, value=values, color="rgba(15,118,110,.35)")))
    fig_graph.update_layout(height=360, margin=dict(l=0, r=0, t=12, b=0))
    st.plotly_chart(fig_graph, use_container_width=True)
    st.caption("World Graph roadmap: add causal evidence, time windows, geographic scope, source links, and uncertainty to every edge.")

with world_tabs[3]:
    st.markdown("**Ask the World**")
    st.write("Type a question about a world issue. The current prototype responds from the live hazard layer, operational data, and clearly labeled roadmap knowledge.")
    if "world_chat" not in st.session_state:
        st.session_state.world_chat = []
    for message in st.session_state.world_chat:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    st.caption("Try: **Where are the current earthquake signals?** · **What resources need attention?** · **What are the biggest emerging problems in Asia?**")
    ask = st.chat_input("Ask about earthquakes, climate, resources, shortages, Asia, or emerging problems", key="world_chat_input")
    if ask:
        st.session_state.world_chat.append({"role": "user", "content": ask})
        q = ask.lower()
        if "earthquake" in q:
            answer = "### Earthquake signals\n\nThe live hazard layer uses the **USGS Earthquake Catalog**. Open the Global Intelligence section below to inspect worldwide events with magnitude, location, time, depth, and source attribution. The feed is observational; it is not a prediction of future earthquakes.\n\n**Evidence:** live USGS feed."
        elif any(word in q for word in ["resource", "shortage", "food", "water", "medicine", "supply"]):
            answer = f"### Resource situation\n\nIn the current operational view, **{critical} critical request(s)** and **{open_requests} open request(s)** affect **{people_impacted:,} people** under the selected filters. Use the triage queue and Recommended dispatches to see priority locations and suggested quantities.\n\n**Evidence:** CrisisBridge prototype request and inventory data."
        elif any(word in q for word in ["asia", "emerging", "global problem", "world issue", "biggest problem"]):
            answer = "### Emerging world issues\n\nThe strongest evidence currently available in this prototype covers **hazards, emergency shortages, and location-level weather context**. The next verified adapters are climate hazards, health, agriculture, economy, energy, supply chain, internet infrastructure, cities, and science.\n\nI will not invent a ranking for a domain that is not yet connected. **Evidence status:** live for USGS/Open-Meteo; prototype or roadmap for the other domains."
        elif any(word in q for word in ["climate", "weather", "heat", "rain", "flood"]):
            answer = "### Climate and weather\n\nSearch a country, city, district, block, or village in the Global Intelligence section. CrisisBridge will geocode the place with OpenStreetMap Nominatim and retrieve current weather context from Open-Meteo. This is context, not an official warning service."
        else:
            answer = "### What I can answer now\n\nAsk me about **earthquake signals, climate or weather context, resources, shortages, Asia, or emerging world problems**. For every answer, CrisisBridge labels whether the evidence is live, prototype, architecture-stage, or roadmap-stage."
        st.session_state.world_chat.append({"role": "assistant", "content": answer})
        st.rerun()

if critical:
    st.markdown(f'<div class="alert"><strong>Immediate attention:</strong> {critical} critical request(s) require triage. Review the highest-priority locations below.</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
c1.metric("People in filtered requests", f"{people_impacted:,}")
c2.metric("Open requests", f"{open_requests:,}")
c3.metric("Critical requests", f"{critical:,}")
c4.metric("Open shelters", f"{active_shelters:,}")

st.markdown('<div class="section-title">Global intelligence layer</div>', unsafe_allow_html=True)
intel_a, intel_b = st.columns([1.2, 1])
with intel_a:
    st.markdown("**Live hazard feed**")
    try:
        earthquakes = fetch_earthquakes(days=7, minimum_magnitude=4.5)
        if earthquakes.empty:
            st.info("No USGS earthquakes matched the current threshold.")
        else:
            eq_map = earthquakes.rename(columns={"latitude": "lat", "longitude": "lon"})
            fig_eq = px.scatter_geo(eq_map, lat="lat", lon="lon", size="severity", color="severity", hover_name="place", hover_data={"hazard": True, "time": True, "depth_km": True, "lat": False, "lon": False}, color_continuous_scale="YlOrRd", projection="natural earth", title="USGS earthquakes: last 7 days", height=430)
            fig_eq.update_layout(margin=dict(l=0, r=0, t=42, b=0))
            st.plotly_chart(fig_eq, use_container_width=True)
            st.caption("Source: USGS Earthquake Hazards Program. Data are live and may be revised.")
    except Exception as exc:
        st.warning(f"Live earthquake feed unavailable: {exc}")

with intel_b:
    st.markdown("**Locate any place in the world**")
    place_query = st.text_input("Search country, city, district, block, or village", placeholder="e.g. Kathmandu, Dharavi, or a village name")
    if place_query:
        try:
            location = geocode_location(place_query)
            if location:
                st.success(location["display_name"])
                st.caption(f"Coordinates: {location['latitude']:.5f}, {location['longitude']:.5f} · {location['source']}")
                weather = fetch_weather(location["latitude"], location["longitude"])
                current = weather.get("current", {})
                w1, w2 = st.columns(2)
                w1.metric("Temperature", f"{current.get('temperature_2m', '—')} °C")
                w2.metric("Wind", f"{current.get('wind_speed_10m', '—')} km/h")
                st.caption("Weather context from Open-Meteo; use official local alerts for decisions.")
            else:
                st.warning("No location match found. Try a nearby city or include the country.")
        except Exception as exc:
            st.warning(f"Location lookup unavailable: {exc}")
    st.markdown("**Humanitarian situation updates**")
    try:
        updates = fetch_reliefweb_updates(limit=6)
        if not updates.empty:
            st.dataframe(updates[["title", "country", "source", "created"]], use_container_width=True, hide_index=True)
            st.caption("Source: ReliefWeb API, a UN OCHA service. Updates may contain partner-owned content.")
    except Exception as exc:
        st.warning(f"ReliefWeb feed unavailable: {exc}")

st.markdown('<div class="section-title">Operational picture</div>', unsafe_allow_html=True)
left, right = st.columns([1.45, 1])
with left:
    map_df = filtered.rename(columns={"latitude": "lat", "longitude": "lon"}).copy()
    if not map_df.empty:
        fig_map = px.scatter_mapbox(
            map_df,
            lat="lat", lon="lon", color="priority", size="people_affected",
            hover_name="location", hover_data={"need_type": True, "status": True, "people_affected": True, "lat": False, "lon": False},
            color_discrete_map={"Critical": "#b91c1c", "High": "#ea580c", "Medium": "#d97706", "Low": "#0f766e"},
            zoom=8.4, center={"lat": 19.08, "lon": 72.88}, height=430,
            mapbox_style="open-street-map", title="Live request priority map",
        )
        fig_map.update_layout(margin=dict(l=0, r=0, t=42, b=0), legend_title_text="Priority")
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.info("No requests match the selected filters.")
with right:
    need_counts = filtered.groupby("need_type", as_index=False)["people_affected"].sum().sort_values("people_affected", ascending=True)
    fig_need = px.bar(need_counts, x="people_affected", y="need_type", orientation="h", color="people_affected", color_continuous_scale="Tealgrn", title="People affected by need type", height=430)
    fig_need.update_layout(margin=dict(l=0, r=0, t=42, b=0), coloraxis_showscale=False, xaxis_title="People", yaxis_title="")
    st.plotly_chart(fig_need, use_container_width=True)

st.markdown('<div class="section-title">Triage queue</div>', unsafe_allow_html=True)
triage = filtered.sort_values(["priority_score", "people_affected"], ascending=False).copy()
triage["priority_score"] = triage["priority_score"].round(0).astype(int)
st.dataframe(
    triage[["request_id", "location", "zone", "need_type", "people_affected", "priority", "priority_score", "status", "reported_at"]].head(12),
    use_container_width=True, hide_index=True,
    column_config={"priority_score": st.column_config.ProgressColumn("Priority score", min_value=0, max_value=100, format="%d")},
)

st.markdown('<div class="section-title">Recommended dispatches</div>', unsafe_allow_html=True)
recommendations = build_resource_recommendations(filtered, resources)
if recommendations.empty:
    st.info("No dispatch recommendations are available for the selected filters.")
else:
    st.dataframe(recommendations, use_container_width=True, hide_index=True)

st.download_button(
    "Download triage queue",
    data=triage.to_csv(index=False).encode("utf-8"),
    file_name="crisisbridge_triage_queue.csv",
    mime="text/csv",
)

st.caption("CrisisBridge is a decision-support prototype. It does not replace trained emergency-management professionals or verified field intelligence.")
