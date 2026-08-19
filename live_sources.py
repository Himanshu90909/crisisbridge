from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pandas as pd
import requests
import streamlit as st

HEADERS = {"User-Agent": "CrisisBridge/1.0 (emergency-intelligence-prototype)"}


def _get_json(url: str, params: dict[str, Any], timeout: int = 15) -> dict[str, Any]:
    response = requests.get(url, params=params, headers=HEADERS, timeout=timeout)
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=600, show_spinner=False)
def fetch_earthquakes(days: int = 7, minimum_magnitude: float = 4.5) -> pd.DataFrame:
    end = datetime.now(timezone.utc)
    start = end - pd.Timedelta(days=days)
    payload = _get_json(
        "https://earthquake.usgs.gov/fdsnws/event/1/query",
        {
            "format": "geojson",
            "starttime": start.strftime("%Y-%m-%dT%H:%M:%S"),
            "endtime": end.strftime("%Y-%m-%dT%H:%M:%S"),
            "minmagnitude": minimum_magnitude,
            "orderby": "time",
            "limit": 500,
        },
    )
    rows = []
    for feature in payload.get("features", []):
        props = feature.get("properties", {})
        coords = feature.get("geometry", {}).get("coordinates", [None, None, None])
        rows.append({
            "event_id": feature.get("id"),
            "hazard": "Earthquake",
            "title": props.get("title", "Earthquake"),
            "place": props.get("place", "Unknown location"),
            "severity": float(props.get("mag") or 0),
            "time": pd.to_datetime(props.get("time"), unit="ms", utc=True),
            "latitude": coords[1],
            "longitude": coords[0],
            "depth_km": coords[2],
            "url": props.get("url"),
            "source": "USGS Earthquake Hazards Program",
        })
    return pd.DataFrame(rows)


@st.cache_data(ttl=900, show_spinner=False)
def fetch_reliefweb_updates(limit: int = 20) -> pd.DataFrame:
    try:
        payload = _get_json(
            "https://api.reliefweb.int/v1/reports",
            {
                "appname": "crisisbridge",
                "limit": limit,
                "sort[]": "date:desc",
                "fields[include][]": ["title", "date.created", "source.name", "primary_country.name", "url", "status"],
            },
        )
    except requests.HTTPError:
        # ReliefWeb currently returns HTTP 410 for this endpoint in some environments.
        # Return an empty frame so the dashboard continues with other live sources.
        return pd.DataFrame(columns=["title", "country", "source", "created", "url"])
    rows = []
    for item in payload.get("data", []):
        fields = item.get("fields", {})
        countries = fields.get("primary_country") or []
        country = countries[0].get("name") if countries else "Global"
        sources = fields.get("source") or []
        source = sources[0].get("name") if sources else "ReliefWeb"
        rows.append({
            "title": fields.get("title", "Humanitarian update"),
            "country": country,
            "source": source,
            "created": fields.get("date", {}).get("created"),
            "url": fields.get("url"),
        })
    return pd.DataFrame(rows)


@st.cache_data(ttl=3600, show_spinner=False)
def geocode_location(query: str) -> dict[str, Any] | None:
    if not query.strip():
        return None
    payload = requests.get(
        "https://nominatim.openstreetmap.org/search",
        params={"q": query, "format": "geocodejson", "addressdetails": 1, "limit": 1},
        headers=HEADERS,
        timeout=15,
    )
    payload.raise_for_status()
    features = payload.json().get("features", [])
    if not features:
        return None
    feature = features[0]
    coords = feature.get("geometry", {}).get("coordinates", [None, None])
    props = feature.get("properties", {})
    return {
        "display_name": props.get("label", query),
        "latitude": coords[1],
        "longitude": coords[0],
        "geocoding": props.get("geocoding", {}),
        "source": "OpenStreetMap Nominatim",
    }


@st.cache_data(ttl=900, show_spinner=False)
def fetch_weather(latitude: float, longitude: float) -> dict[str, Any]:
    payload = _get_json(
        "https://api.open-meteo.com/v1/forecast",
        {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,weather_code",
            "daily": "precipitation_sum,wind_gusts_10m_max,temperature_2m_max",
            "forecast_days": 3,
            "timezone": "auto",
        },
    )
    return payload
