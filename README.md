# CrisisBridge

## Emergency Response Intelligence for Resource Allocation

CrisisBridge is a Streamlit decision-support prototype for coordinating shelters, hospitals, emergency supplies, volunteers, and citizen requests during floods, earthquakes, fires, cyclones, and other disasters.

> **Mission:** make every emergency resource count by helping response teams understand which requests are most urgent and where limited supplies should go first.

## The problem

Disaster response teams often work with fragmented reports from shelters, hospitals, volunteers, local authorities, and citizens. Without a shared operational view, one location may receive excess supplies while another location faces a critical shortage. CrisisBridge creates a single, visual triage workspace for prioritizing requests and recommending dispatches.

This repository uses **synthetic demonstration data**. It is not connected to a live emergency service and must not be used to direct real-world response operations without professional verification.

## What the application demonstrates

| Capability | Implementation |
|---|---|
| Interactive data application | Streamlit layout, sidebar filters, metrics, tables, downloads |
| Data engineering | CSV ingestion, datetime parsing, filtering, grouped summaries |
| Geographic intelligence | Interactive Mapbox/OpenStreetMap request map with priority colors |
| Decision support | Weighted request-priority scoring and dispatch recommendations |
| Data visualization | Plotly map, bar chart, operational KPI cards |
| Machine-learning-ready design | Clear extension point for shortage forecasting and risk prediction |
| Product thinking | Defined users, workflow, safety disclaimer, and measurable operational outputs |
| Engineering practice | Modular utilities, reproducible dependencies, synthetic fixtures, and documented roadmap |

## Core workflow

1. Load requests, shelters, hospitals, and resource inventory.
2. Filter the operational picture by status, need type, and response zone.
3. Calculate a transparent priority score using population impact, urgency, need type, and verification status.
4. Review the highest-priority requests on the map and in the triage queue.
5. Compare unmet needs with available inventory.
6. Review recommended dispatches and download the triage queue for coordination.

## Project structure

```text
crisisbridge/
├── app.py
├── requirements.txt
├── README.md
├── data/
│   ├── emergency_requests.csv
│   ├── hospitals.csv
│   ├── resources.csv
│   └── shelters.csv
└── utils/
    └── analytics.py
```

## Run locally

```bash
git clone <your-repository-url>
cd crisisbridge
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL printed by Streamlit, normally `http://localhost:8501`.

## Example outputs

The dashboard provides an emergency command view with the following operational outputs:

- people affected by the selected request set;
- open and critical requests;
- open shelter count;
- interactive request-priority map;
- needs ranked by affected population;
- sortable triage queue;
- recommended dispatch quantity and source warehouse; and
- downloadable CSV triage report.

## Roadmap

The next production-oriented iterations would add role-based access, PostgreSQL storage, audited status changes, verified geospatial feeds, multilingual request intake, SMS notifications, duplicate-request detection, route optimization, and a time-series model that forecasts shelter shortages over the next 24–48 hours.

## Safety and responsible use

CrisisBridge is a prototype for research, education, and portfolio demonstration. Emergency decisions must be made by trained authorities using verified field intelligence. The priority score is transparent but simplified; it must not be treated as an automated determination of whose life is more valuable.

## License

This project is released under the MIT License. Add a `LICENSE` file before public distribution if you want to formalize the licensing terms.
