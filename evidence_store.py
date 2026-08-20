"""Evidence records, provenance, deduplication, and retrieval for CrisisBridge.

The JSONL store is suitable for a local/demo deployment. Production should replace
it with a durable database or object store while preserving this record schema.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Any, Iterable

STORE_PATH = Path(__file__).with_name("evidence_records.jsonl")

@dataclass
class EvidenceRecord:
    record_id: str
    event_key: str
    domain: str
    title: str
    summary: str
    location: str
    country: str
    source_name: str
    source_url: str
    source_tier: str
    observed_at: str
    fetched_at: str
    freshness: str = "unknown"
    severity: str = "unknown"
    affected_people: int | None = None
    deaths: int | None = None
    injuries: int | None = None
    missing: int | None = None
    confidence: str = "unverified"
    raw: dict[str, Any] = field(default_factory=dict)


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")[:80]


def make_event_key(domain: str, title: str, location: str) -> str:
    base = f"{_slug(domain)}|{_slug(title)}|{_slug(location)}"
    return sha256(base.encode("utf-8")).hexdigest()[:20]


def new_record(*, domain: str, title: str, summary: str, location: str, country: str,
               source_name: str, source_url: str, source_tier: str, observed_at: str,
               **kwargs: Any) -> EvidenceRecord:
    now = datetime.now(timezone.utc).isoformat()
    event_key = make_event_key(domain, title, location)
    record_id = sha256(f"{event_key}|{source_name}|{observed_at}".encode()).hexdigest()[:24]
    return EvidenceRecord(record_id=record_id, event_key=event_key, domain=domain,
        title=title, summary=summary, location=location, country=country,
        source_name=source_name, source_url=source_url, source_tier=source_tier,
        observed_at=observed_at, fetched_at=now, **kwargs)


def save_records(records: Iterable[EvidenceRecord], path: Path = STORE_PATH) -> int:
    existing = {r.record_id for r in load_records(path)}
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("a", encoding="utf-8") as handle:
        for record in records:
            if record.record_id in existing:
                continue
            handle.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")
            existing.add(record.record_id)
            count += 1
    return count


def load_records(path: Path = STORE_PATH) -> list[EvidenceRecord]:
    if not path.exists():
        return []
    records: list[EvidenceRecord] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            records.append(EvidenceRecord(**json.loads(line)))
        except (TypeError, json.JSONDecodeError):
            continue
    return records


def retrieve(query: str, records: Iterable[EvidenceRecord], limit: int = 8) -> list[EvidenceRecord]:
    terms = set(re.findall(r"[a-z0-9]+", query.lower()))
    scored: list[tuple[int, EvidenceRecord]] = []
    for record in records:
        haystack = " ".join([record.domain, record.title, record.summary, record.location, record.country]).lower()
        score = sum(1 for term in terms if term in haystack)
        if score:
            scored.append((score, record))
    return [record for _, record in sorted(scored, key=lambda item: item[0], reverse=True)[:limit]]


def format_evidence_context(records: Iterable[EvidenceRecord]) -> str:
    rows = []
    for r in records:
        rows.append({"event": r.title, "domain": r.domain, "location": r.location,
                     "summary": r.summary, "source": r.source_name, "source_url": r.source_url,
                     "observed_at": r.observed_at, "affected_people": r.affected_people,
                     "deaths": r.deaths, "confidence": r.confidence})
    return json.dumps(rows, ensure_ascii=False, indent=2)
