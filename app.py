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
from disaster_agent import classify_disaster_question, render_disaster_report, supported_prompt
from gemini_engine import ask_gemini, gemini_available, gemini_status
from evidence_store import load_records, retrieve, save_records, format_evidence_context
from india_sources import fetch_sachet_alerts

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
world_tabs = st.tabs(["Global Pulse", "Problem Radar", "World Graph", "Ask the World", "AI Evidence Lab"])
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

    st.caption("Try: **Assam me baadh aayi hai ya nahi?** · **Where are the current earthquake signals?** · **Which official alerts are active in India?**")
    refresh_india = st.checkbox("Refresh official India evidence before answering", value=False, help="Fetches the public NDMA SACHET page and stores normalized evidence records. It does not invent impact or casualty figures.")
    ask = st.chat_input("Ask about floods, earthquakes, cyclone, alerts, deaths, affected people, or resources", key="world_chat_input")
    if ask:
        st.session_state.world_chat.append({"role": "user", "content": ask})
        if refresh_india and any(term in ask.lower() for term in ["india", "assam", "flood", "baadh", "cyclone", "earthquake", "alert", "disaster"]):
            india_records, india_meta = fetch_sachet_alerts()
            if india_records:
                save_records(india_records)
        matched_evidence = retrieve(ask, load_records(), limit=6)
        evidence_context = format_evidence_context(matched_evidence) if matched_evidence else "No matching stored evidence records."
        q = ask.lower()
        intent = classify_disaster_question(ask)
        death_requested = any(word in q for word in ["die", "died", "death", "deaths", "fatalit", "casualt"])
        live_eq_count = "not available"
        live_eq_peak = "not available"
        live_eq_place = "not available"
        if intent.domain == "earthquake":
            try:
                live_eq = fetch_earthquakes(days=7, minimum_magnitude=4.5)
                live_eq_count = len(live_eq)
                if not live_eq.empty:
                    peak = live_eq.sort_values("severity", ascending=False).iloc[0]
                    live_eq_peak = f"M{peak['severity']:.1f}"
                    live_eq_place = str(peak["place"])
            except Exception:
                pass
            deaths_line = "**Deaths/casualties:** Not reported by the connected USGS event feed; do not infer deaths from magnitude." if death_requested else "**Deaths/casualties:** Not provided by this hazard feed."
            answer = f"### Earthquake situation\n\n**What is happening:** The live USGS layer currently contains **{live_eq_count} event(s)** in the last seven days at or above M4.5. The highest-magnitude event in the retrieved set is **{live_eq_peak}** near **{live_eq_place}**.\n\n**Affected people:** Not reported by the connected event feed. Affected population requires a separate exposure or humanitarian source.\n\n{deaths_line}\n\n**Evidence status:** Live observational event data; not a forecast.\n\n**Source:** [USGS Earthquake Catalog](https://earthquake.usgs.gov/fdsnws/event/1/)\n\n**Recommended next step:** Open the live hazard map, select the event, compare with official local alerts, and verify casualty figures through local authorities or humanitarian situation reports."
        elif any(word in q for word in ["resource", "shortage", "food", "water", "medicine", "supply", "help"]):
            deaths_line = "**Deaths/casualties:** Not reported in the connected CrisisBridge operational dataset." if death_requested else ""
            answer = f"### Resource and humanitarian situation\n\n**Current operational snapshot:** The selected view contains **{critical} critical request(s)**, **{open_requests} open request(s)**, and **{people_impacted:,} affected people**.\n\n**Affected groups:** The dashboard can show locations, need types, people affected, request status, and priority. It does not identify private individuals.\n\n**Resource action:** The system suggests a dispatch location, resource type, quantity, and source warehouse. These are decision-support recommendations, not autonomous orders.\n\n{deaths_line}\n\n**Evidence status:** Prototype request and inventory data.\n\n**Recommended next step:** Review verified requests first, compare inventory, confirm the destination with a responsible coordinator, and record the completed dispatch."
        elif any(word in q for word in ["conflict", "war", "violence", "health", "disease", "outbreak", "epidemic", "pandemic", "agriculture", "crop", "drought", "energy", "oil", "gas", "economy", "inflation", "market", "stock", "supply chain", "internet", "outage", "housing", "city", "science"]):
            domain = "public health" if any(word in q for word in ["health", "disease", "outbreak", "epidemic", "pandemic"]) else "conflict and violence" if any(word in q for word in ["conflict", "war", "violence"]) else "economy, markets, and supply chains"
            answer = f"### {domain.title()} intelligence\n\n**Domain recognized:** The World Agent understands this as a {domain} question.\n\n**Live data status:** A dedicated authoritative adapter for this domain is not yet connected in the current prototype, so I cannot responsibly provide a current location, affected population, or death count.\n\n**Deaths/casualties:** Not reported by a connected source. The agent must never estimate deaths from headlines, severity scores, or population totals.\n\n**Production source path:** Use a domain-specific source such as WHO or a national health authority for outbreaks, UCDP for conflict fatalities, EM-DAT/GDACS for disaster impacts, or official economic and infrastructure providers for other domains.\n\n**Recommended next step:** Specify a place and date range. The next version should retrieve source records, show the timestamp and geography, compare conflicting counts, and label figures as confirmed, reported, estimated, cumulative, or provisional."
        elif any(word in q for word in ["asia", "emerging", "global problem", "world issue", "biggest problem", "risk"]):
            answer = "### Global problem scan\n\n**Connected evidence:** Live coverage currently includes earthquake activity and location-level weather context, plus the operational emergency-request dataset.\n\n**Affected people and deaths:** These figures are not globally available from one connected source. The agent will show **Not reported** rather than inventing numbers, and will distinguish affected population from confirmed deaths.\n\n**Domains in the expansion plan:** climate, disasters, public health, conflict, food and agriculture, water, energy, economy, markets, supply chain, internet infrastructure, cities, and science. Each domain needs its own verified adapter, timestamp, geography, and uncertainty model.\n\n**Recommended next step:** Ask for one domain, region, and time period—for example, *What conflict fatalities were reported in region X during month Y?*—so the agent can return a source-bounded answer."
        elif "assam" in q and any(word in q for word in ["flood", "flooding", "baadh", "water", "inundat"]):
            answer = "### Assam flood status\n\n**Short answer: Haan — the latest accessible report says active flooding was reported in Assam.**\n\n**Latest reported situation:** The cited report described flooding across **10 districts, 28 revenue circles, and 456 villages**, with **137,590 people affected** and **11,933.46 hectares of crops submerged**. It named Golaghat, Sivasagar, Hojai, Darrang, Lakhimpur, Jorhat, Karbi Anglong, Charaideo, Nagaon, and Biswanath.\n\n**Deaths:** The same report gave a reported total of **100 deaths**, but this figure is **as of 10 August 2026**, not a guaranteed real-time total.\n\n**Weather risk:** An India Meteorological Department bulletin issued on **19 August 2026** forecast widespread rainfall over Assam and Meghalaya during 19–22 August and 25 August, with isolated heavy rainfall possible during 19–25 August. This supports continuing rain risk but does not by itself confirm new inundation or deaths.\n\n**Evidence status:** Reported flood situation plus official weather forecast; freshness is limited because the impact report is not a live ASDMA/DRIMS feed.\n\n**Sources:** [NDTV Assam flood report](https://www.ndtv.com/india-news/assam-flood-death-count-rises-to-100-over-1-3-lakh-people-affected-11888931) · [India Meteorological Department bulletin](https://internal.imd.gov.in/section/nhac/dynamic/allindianew.pdf) · [ASDMA official portal](https://asdma.assam.gov.in/)\n\n**Recommended next step:** For a truly current answer, connect the ASDMA/DRIMS flood bulletin directly and display its retrieval time. For safety decisions, follow ASDMA, district administration, IMD, and local emergency instructions."
        elif intent.domain == "flood":
            answer = render_disaster_report(
                ask,
                intent,
                status="No location-specific live flood impact record is attached yet",
                affected_people=None,
                deaths=None,
                resources=["water, food, medicine, shelter, rescue, and communications"],
                source_links=[("ASDMA", "https://asdma.assam.gov.in/"), ("GDACS", "https://gdacs.org/"), ("ReliefWeb", "https://reliefweb.int/")],
                evidence_status="Disaster domain recognized; connect the current official bulletin before treating the report as live",
                confidence="Low without a named location and current impact bulletin",
                limitations="Weather forecasts do not prove inundation, and no casualty figure is shown unless an impact source explicitly reports it.",
            )
        elif any(word in q for word in ["climate", "weather", "heat", "rain"]):
            answer = "### Climate and weather context\n\nSearch a country, city, district, block, or village in the Global Intelligence section. CrisisBridge uses OpenStreetMap Nominatim to retrieve the place and Open-Meteo to retrieve current weather context.\n\n**Affected people:** Not reported by the weather endpoint.\n\n**Deaths/casualties:** Not reported by the connected weather endpoint; never infer casualties from temperature, rainfall, or wind alone.\n\n**Important limitation:** Current weather context is not the same as a climate trend, flood forecast, drought assessment, or official warning.\n\n**Sources:** [Open-Meteo](https://open-meteo.com/en/docs) · [OpenStreetMap Nominatim](https://nominatim.org/release-docs/latest/api/Search/)\n\n**Recommended next step:** Search the location, compare conditions with official local warnings, and use a humanitarian or disaster-impact source for affected-population and casualty figures."
        elif any(word in q for word in ["how", "what can you", "capability", "source", "data"]):
            answer = "### World Agent capabilities\n\nThe agent can recognize questions across disasters, climate, health, conflict, food, water, energy, economy, markets, supply chain, internet, cities, science, and emergency resources.\n\nFor each domain, a production answer should return: **problem type, location, event time, current status, affected population, deaths, injuries, missing people, source, timestamp, confidence, limitations, and recommended verification**. Unknown values appear as **Not reported by the connected source**, never as zero.\n\nThe current prototype has live adapters for earthquakes, geocoding, and weather context. Other domains are recognized but marked as awaiting verified adapters."
        elif intent.domain != "general":
            answer = render_disaster_report(
                ask,
                intent,
                status="Recognized, but a current domain-specific impact record is not attached",
                source_links=[("GDACS", "https://gdacs.org/"), ("ReliefWeb", "https://reliefweb.int/")],
                evidence_status="Domain recognized; source adapter required for live impact figures",
                confidence="Low until a current source record is attached",
                limitations="The agent will not invent affected people, deaths, injuries, or responders. Add a location and time range for a source-bounded answer.",
            )
        else:
            answer = "### Ask about any world problem\n\nInclude a **problem**, **place**, and **time period**. Examples: *How many people died in the latest earthquake?* *What health outbreaks are reported in Africa this month?* *What conflict casualties are reported in region X?* *Which areas face food or water stress?*\n\n" + supported_prompt() + "\n\nThe agent will return source status, affected population, deaths if explicitly reported, uncertainty, and a recommended verification step. It will say **Not reported** when no connected authority provides a figure."
        if matched_evidence:
            answer += "\n\n### Retrieved evidence records\n\n" + evidence_context + "\n\nThese records are source-linked observations. They do not override newer official bulletins, and missing casualty fields remain **Not reported**."
        else:
            answer += "\n\n### Evidence store status\n\nNo matching saved official evidence record was found for this wording. Enable **Refresh official India evidence** and ask with a location, event type, and time period."
        st.session_state.world_chat.append({"role": "assistant", "content": answer})
        st.rerun()

with world_tabs[4]:
    st.markdown("**AI Evidence Lab — Gemini-powered multimodal review**")
    st.caption("Use a session-only Gemini key or hosting secrets. Choose the camera purpose before capturing evidence. Do not record private, identifying, or unsafe material without consent.")
    if "ai_history" not in st.session_state:
        st.session_state.ai_history = []
    if "gemini_session_key" not in st.session_state:
        st.session_state.gemini_session_key = ""
    with st.expander("Gemini API configuration", expanded=not gemini_available()):
        ui_key = st.text_input("Gemini API key (session only)", type="password", value=st.session_state.gemini_session_key, help="The key is kept only in this Streamlit session. For deployment, prefer Streamlit Secrets instead of typing it here.")
        remember_key = st.checkbox("Use this key for the current session", value=False)
        if remember_key:
            st.session_state.gemini_session_key = ui_key.strip()
        st.caption("For Streamlit Cloud, configure GEMINI_API_KEY in App settings → Secrets. The deterministic fallback works without a key.")
    with st.form("ai_evidence_form", clear_on_submit=False):
        ai_question = st.text_area("Question", placeholder="Example: Is this area showing flood damage, and what should responders verify?", height=90)
        camera_mode = st.selectbox("Camera purpose", ["Front camera — reporter/selfie context", "Rear camera — field scene or damage context"], help="The browser may show its own camera selector. This label tells Gemini how to interpret the captured evidence.")
        image_evidence = st.camera_input("Capture camera evidence (optional)", help="Use the front camera for reporter context or the rear camera for a field scene. Obtain consent before recording people.")
        audio_widget = getattr(st, "audio_input", None)
        audio_evidence = audio_widget("Voice report (optional)") if audio_widget else None
        submitted = st.form_submit_button("Analyze evidence", type="primary")
    if submitted and ai_question.strip():
        context = {
            "source_status": "USGS/Open-Meteo live adapters plus CrisisBridge prototype request data",
            "filtered_request_count": open_requests,
            "critical_request_count": critical,
            "people_impacted": people_impacted,
            "data_warning": "Synthetic operations data; verify all real-world decisions with authorities.",
            "camera_purpose": camera_mode,
        }
        result = ask_gemini(
            ai_question.strip(),
            context,
            image_bytes=image_evidence.getvalue() if image_evidence else None,
            audio_bytes=audio_evidence.getvalue() if audio_evidence else None,
            api_key=st.session_state.gemini_session_key or ui_key.strip() or None,
        )
        if result is None:
            result = render_disaster_report(
                ai_question.strip(),
                classify_disaster_question(ai_question),
                status="Gemini key not configured; returned safe source-bounded fallback",
                affected_people=people_impacted,
                resources=["water", "food", "medicine", "shelter", "rescue"],
                evidence_status="Local deterministic fallback; no external AI call",
                confidence="Medium for dashboard counts; low for unconnected world facts",
                limitations="Configure GEMINI_API_KEY in Streamlit secrets to enable Gemini reasoning and multimodal review.",
            )
        st.session_state.ai_history.append({"question": ai_question.strip(), "answer": result})
    for item in reversed(st.session_state.ai_history):
        with st.expander(f"Question: {item['question']}", expanded=True):
            st.markdown(item["answer"])
    active_key = st.session_state.gemini_session_key or ui_key.strip()
    st.info("Gemini status: " + gemini_status(active_key))
    st.markdown("**Editable triage snapshot**")
    st.data_editor(filtered.head(12), use_container_width=True, hide_index=True, disabled=["request_id", "priority_score"], key="triage_editor")

if critical:
    st.markdown(f'<div class="alert"><strong>Immediate attention:</strong> {critical} critical request(s) require triage. Review the highest-priority locations below.</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
c1.metric("People in filtered requests", f"{people_impacted:,}", delta="filtered live view")
c2.metric("Open requests", f"{open_requests:,}", delta=f"{critical} critical")
c3.metric("Critical requests", f"{critical:,}", delta="priority queue", delta_color="inverse")
c4.metric("Open shelters", f"{active_shelters:,}", delta="operational")

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
