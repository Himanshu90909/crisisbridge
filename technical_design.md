# CrisisBridge Sentinel Technical Design

## Data flow

The application loads the demonstration operational tables through Pandas, computes priority scores, and exposes filtered views through Streamlit widgets. Live adapters retrieve earthquake, geocoding, and weather observations with timeouts and graceful fallbacks. The disaster router classifies a question into a domain and the report builder renders a consistent Markdown schema.

The optional AI path receives a dynamic context object containing the current filtered request counts, source status, and safety warning. The Gemini system prompt requires direct answers, evidence labels, source context, uncertainty, and recommended verification. Camera and audio uploads are passed as optional multimodal parts. If no key is configured or the request fails, the deterministic report engine returns a safe source-bounded fallback.

## API integration strategy

| Source | Purpose | Credential policy | Failure policy |
|---|---|---|---|
| USGS | Global earthquake observations | Public endpoint | Show last successful observation or unavailable |
| Open-Meteo | Current weather context | Public endpoint for normal use | Show source unavailable and never infer casualties |
| Nominatim | Location search | Public endpoint with rate limits | Ask the user for a more precise location |
| GDACS / ReliefWeb / ASDMA | Disaster and humanitarian impact | Public or source-specific access | Label adapter status and preserve source links |
| Gemini | Tailored text and multimodal analysis | Optional `GEMINI_API_KEY` secret | Deterministic fallback |

## State and API-call optimization

`st.session_state.world_chat` preserves conversation history across reruns. `st.session_state.ai_history` preserves submitted AI Evidence Lab reports. The multimodal workspace uses `st.form` so a question, camera capture, and audio capture are submitted together rather than triggering multiple calls while users are filling the form. Live adapters should be wrapped with Streamlit caching in the production version when refresh frequency and provider terms allow it.

## Evidence and casualty logic

Every report separates observations, forecasts, source-reported impacts, estimates, and unknowns. Deaths, injuries, missing people, and affected populations are never derived from magnitude, rainfall, severity scores, population totals, or visual appearance. When a source does not provide a number, the UI says **Not reported by the connected source**. When sources disagree, the production ingestion layer should retain each source figure with its timestamp rather than silently averaging them.

## Deployment

The entrypoint is `app.py`. Dependencies are declared in `requirements.txt`. Gemini is optional, so the public demo works without secrets. For Streamlit Community Cloud, add `GEMINI_API_KEY` under App settings → Secrets to enable the AI Evidence Lab’s Gemini path.
