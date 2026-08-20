"""Official India disaster-source adapters.

Adapters return normalized EvidenceRecord objects and never fabricate impact or
casualty values. Endpoints may change; failures are returned as status metadata.
"""
from __future__ import annotations

from datetime import datetime, timezone
import os
import re
from typing import Any

import requests
from bs4 import BeautifulSoup

from evidence_store import EvidenceRecord, new_record

SACHET_URL = "https://sachet.ndma.gov.in/"
SACHET_FEED_URL = "https://sachet.ndma.gov.in/CapFeed"
IMD_API_REFERENCE = "https://api.imd.gov.in/public/api_reference.html"
NDMA_GIS_URL = "https://gis-dm.ndma.gov.in/server/rest/services"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_get(url: str, timeout: int = 15) -> requests.Response | None:
    try:
        return requests.get(url, timeout=timeout, headers={"User-Agent": "CrisisBridge/1.0"})
    except requests.RequestException:
        return None


def fetch_sachet_alerts(limit: int = 30) -> tuple[list[EvidenceRecord], dict[str, Any]]:
    """Parse visible official SACHET alert rows as a best-effort live adapter.

    The portal exposes CAP/RSS functionality, but the public page does not always
    expose a stable XML URL. A configurable SACHET_CAP_URL can be used when an
    authorized feed URL is available.
    """
    url = os.getenv("SACHET_CAP_URL", SACHET_FEED_URL)
    response = _safe_get(url)
    meta = {"source": "NDMA SACHET", "url": url, "status": "unavailable", "records": 0}
    if response is None or response.status_code >= 400:
        return [], meta
    soup = BeautifulSoup(response.text, "html.parser")
    text = " ".join(soup.stripped_strings)
    # Prefer visible alert-like labels; exact fields depend on portal rendering.
    patterns = re.findall(r"(Flood|Cyclone|Earthquake|Landslide|Lightning|Thunderstorm|Heat Wave|Fire|Rain|Tsunami)\s+([^|]{3,140})", text, flags=re.I)
    records: list[EvidenceRecord] = []
    seen: set[str] = set()
    for domain, detail in patterns[:limit]:
        detail = re.sub(r"\s+", " ", detail).strip(" -:")
        if detail in seen:
            continue
        seen.add(detail)
        records.append(new_record(domain=domain.lower(), title=f"SACHET {domain} alert",
            summary=detail, location=detail, country="India", source_name="NDMA SACHET",
            source_url=SACHET_URL, source_tier="primary-government", observed_at=_now(),
            freshness="live-page", confidence="source-reported"))
    meta.update({"status": "ok", "records": len(records)})
    return records, meta


def fetch_imd_json(endpoint: str, label: str, params: dict[str, Any] | None = None) -> tuple[dict[str, Any] | list[Any] | None, dict[str, Any]]:
    response = _safe_get(endpoint)
    meta = {"source": "India Meteorological Department", "url": endpoint, "label": label, "status": "unavailable"}
    if response is None or response.status_code >= 400:
        return None, meta
    try:
        payload = response.json()
    except ValueError:
        return None, meta
    meta.update({"status": "ok", "reference": IMD_API_REFERENCE})
    return payload, meta


def fetch_ndma_gis_index() -> tuple[dict[str, Any] | None, dict[str, Any]]:
    endpoint = NDMA_GIS_URL + "?f=pjson"
    response = _safe_get(endpoint)
    meta = {"source": "NDMA GIS", "url": endpoint, "status": "unavailable"}
    if response is None or response.status_code >= 400:
        return None, meta
    try:
        payload = response.json()
    except ValueError:
        return None, meta
    meta["status"] = "ok"
    return payload, meta
