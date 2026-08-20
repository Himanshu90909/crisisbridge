# CrisisBridge Sentinel

```text
╭──────────────────────────────────────────────────────────────╮
│ CRISISBRIDGE SENTINEL                                        │
│ Global disaster intelligence + emergency resource command   │
│ Status: Streamlit prototype · Evidence-aware · AI-ready     │
╰──────────────────────────────────────────────────────────────╯
```

> **Make every emergency resource count.**

CrisisBridge Sentinel is a B.Tech Streamlit and AI capstone project for understanding disasters, locating affected places, reviewing source-backed impact information, and coordinating emergency resources. It combines Pandas data pipelines, Plotly visualizations, free public data sources, reusable disaster-domain routing, optional Gemini multimodal analysis, and an explicit safety policy for casualty figures.

## Live demo and repository

| Resource | Link |
|---|---|
| Live app | [Open CrisisBridge](https://8501-ifi6u98evac6sbkax8ox3-4da1dcc5.sg1.manus.computer) |
| GitHub | [Himanshu90909/crisisbridge](https://github.com/Himanshu90909/crisisbridge) |
| Entry point | `app.py` |

The current live link is a temporary demonstration runtime. For a permanent release, deploy the repository on Streamlit Community Cloud, Render, or Hugging Face Spaces.

## Product experience

The visitor can move through **Global Pulse**, **Problem Radar**, **World Graph**, and **Ask the World**. Ask the World is the unified evidence workspace: users can enter a Gemini key, capture front or rear camera evidence, record an audio situation report, attach a PDF/TXT/CSV/JSON/DOCX bulletin, and ask a location-specific disaster question in one conversation. The command center includes KPI cards with deltas, priority maps, triage tables, resource recommendations, download controls, and an editable triage snapshot.

The World Agent accepts questions such as:

```text
Bhai batao ki Assam mein baadh aayi hai ya nahi?
What happened in the latest earthquake?
Which villages are affected by this flood?
How many deaths were reported, and what is the source date?
Who is responding and which resources are needed?
```

The answer engine separates live observations, forecasts, reported impacts, unknowns, confidence, limitations, sources, and recommended verification. It never turns missing casualty data into zero.

## Capstone rubric coverage

| Category | Evidence in this repository |
|---|---|
| Technical implementation | Modular Python files, Pandas DataFrames, `st.session_state`, `st.form`, safe fallbacks, compile validation |
| AI and prompts | `gemini_engine.py`, tailored system prompt, dynamic context, optional camera, audio, and document evidence |
| UI and visualization | Tabs, columns, `st.metric` deltas, expanders, Plotly charts, maps, Sankey graph, `st.data_editor`, CSV downloads |
| Deployment | Streamlit entrypoint and cloud-safe `requirements.txt` with no system packages |
| Open-source branding | Terminal-style README, setup commands, project mission, live link, limitations |
| System design | [`docs/architecture.md`](docs/architecture.md), [`docs/technical_design.md`](docs/technical_design.md), source-policy documents |

See [`CAPSTONE_RUBRIC.md`](CAPSTONE_RUBRIC.md) for the full evaluation mapping and demo script.

## Architecture

```text
Streamlit UI
   ├── Global Pulse / Radar / Graph
   └── Ask the World chat + session history + camera + audio + documents
          │
                 │
          ├── Live source adapters: USGS, Open-Meteo, Nominatim
          ├── Disaster intent router + structured report engine
          ├── Optional Gemini text / vision / audio / document analysis
          └── Evidence, freshness, confidence, and casualty safeguards
```

Open the full Mermaid diagram at [`docs/architecture.md`](docs/architecture.md) and the data-flow specification at [`docs/technical_design.md`](docs/technical_design.md).

## Repository layout

```text
crisisbridge/
├── app.py                    # Streamlit UI and workflows
├── analytics.py              # Pandas loading, scoring, filtering, dispatch logic
├── disaster_agent.py         # Domain router and long-form disaster reports
├── gemini_engine.py          # Optional Gemini prompt and multimodal adapter
├── live_sources.py           # Free public data adapters
├── data/                     # Synthetic demonstration operational data
├── docs/                     # Architecture and technical design
├── CAPSTONE_RUBRIC.md        # Rubric mapping and demo script
├── global_data_sources.md    # Source strategy and coverage notes
├── world_agent_sources.md    # World Agent evidence policy
├── assam_flood_sources.md    # Assam flood evidence and freshness notes
└── requirements.txt          # Cloud dependency manifest
```

## Local setup

```bash
git clone https://github.com/Himanshu90909/crisisbridge.git
cd crisisbridge
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

The application works without a Gemini key through a deterministic, source-bounded fallback. To enable Gemini, create a local `.streamlit/secrets.toml` file:

```toml
GEMINI_API_KEY = "your-key-here"
```

Never commit that file. On Streamlit Community Cloud, add the same secret in the application settings.

## Responsible AI and data policy

CrisisBridge is a decision-support prototype, not an autonomous emergency-dispatch system. The operational CSV files contain synthetic demonstration data and must not be used to direct real-world response. USGS, Open-Meteo, and Nominatim provide live or public context, but no single feed describes every crisis on Earth.

The system reports deaths, injuries, missing people, and affected populations only when a connected source explicitly provides them. If the value is missing, the response says **Not reported by the connected source**. Users must verify urgent information through local authorities, disaster-management agencies, hospitals, and official warnings.

## Development commands

```bash
python validate_capstone.py
python -m compileall -q app.py disaster_agent.py gemini_engine.py
streamlit run app.py
```

## License and attribution

This repository is an educational capstone prototype. Review the terms and attribution requirements of every upstream data provider before production deployment. The project should be extended with authenticated organization registration, scheduled ingestion, PostGIS, moderation, multilingual support, domain-specific casualty feeds, and persistent cloud hosting before real operational use.
