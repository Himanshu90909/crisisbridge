# CrisisBridge Sentinel Architecture

```mermaid
flowchart TD
    U[Visitor / Responder] --> UI[Streamlit UI]
    UI --> P[Global Pulse]
    UI --> R[Problem Radar]
    UI --> G[World Graph]
    UI --> C[Ask the World Chat]
    UI --> M[AI Evidence Lab: Form + Camera + Audio]

    UI --> S[(st.session_state)]
    S --> C
    S --> M

    P --> L[Live Source Adapters]
    C --> D[Disaster Intent Router]
    M --> GE[Gemini Engine]
    M --> FB[Deterministic Safe Fallback]

    L --> USGS[USGS Earthquakes]
    L --> WX[Open-Meteo Weather]
    L --> OSM[OpenStreetMap Nominatim]
    L --> HUM[ReliefWeb / GDACS / ASDMA roadmap]

    D --> F[Flood]
    D --> E[Earthquake]
    D --> X[Cyclone / Fire / Landslide / Drought / Heat]
    D --> H[Health / Conflict / Other]

    F --> REP[Structured Disaster Report]
    E --> REP
    X --> REP
    H --> REP
    GE --> REP
    FB --> REP

    REP --> SAFETY[Evidence, freshness, confidence, casualty safeguards]
    SAFETY --> OUT[Markdown answer + sources + next actions]
```

The architecture separates presentation, state, data adapters, domain routing, optional AI, and deterministic safety logic. The application remains usable when Gemini is not configured or when an upstream source is unavailable.
