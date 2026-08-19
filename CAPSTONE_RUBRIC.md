# CrisisBridge Capstone Rubric Mapping

## Project title

**CrisisBridge Sentinel — Global Disaster Intelligence and Emergency Resource Coordination**

## Problem statement

Emergency information is fragmented across hazard feeds, weather services, humanitarian reports, local requests, shelters, hospitals, and responder updates. CrisisBridge provides a source-aware workspace that helps users understand a crisis, locate it, inspect affected populations and reported casualties, and coordinate resources without inventing unknown facts.

## Evaluation mapping

| Rubric category | Implemented evidence | Score target |
|---|---|---:|
| Technical implementation and architecture | Modular `analytics.py`, `live_sources.py`, `disaster_agent.py`, and `gemini_engine.py`; `st.session_state` for chat and AI history; `st.form` for multimodal analysis; Pandas pipelines; compile validation | 25 |
| AI integration and prompt engineering | Gemini-ready system prompt, dynamic f-string context, source-aware output schema, optional camera and microphone evidence, safe deterministic fallback without a key | 20 |
| UI/UX and visualization | Responsive columns, tabs, KPI cards with deltas, expanders, Plotly maps/charts/Sankey graph, `st.data_editor`, `st.map`-style geospatial layer, downloads | 20 |
| Deployment and cloud engineering | Minimal `requirements.txt`, no local system dependencies, optional secret-based Gemini configuration, Streamlit-compatible entrypoint `app.py` | 15 |
| Open-source branding | Terminal-style README with architecture, setup, Git workflow, environment variables, limitations, and live-app link | 10 |
| System design and documentation | `docs/architecture.md`, `docs/technical_design.md`, source-policy documentation, evidence and casualty rules | 10 |

## Demo script

1. Open **Global Pulse** and explain live versus prototype coverage.
2. Open **Problem Radar** and select earthquake activity or resource shortage.
3. Open **World Graph** and explain the causal chain.
4. Ask: `Bhai batao ki Assam mein baadh aayi hai ya nahi?` and show the direct answer, affected areas, reported deaths, dates, and sources.
5. Open **AI Evidence Lab**, submit a form question, optionally capture a camera image or voice report, and show the deterministic fallback or Gemini response.
6. Edit the triage snapshot in `st.data_editor` and download the operational queue.

## Responsible AI rule

CrisisBridge is a decision-support prototype. It does not replace emergency authorities. The system reports deaths, injuries, missing people, and affected populations only when a connected source explicitly provides those figures. Unknown values are displayed as **Not reported by the connected source**, never as zero.
