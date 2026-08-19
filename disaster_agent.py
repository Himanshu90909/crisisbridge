"""Source-aware disaster question routing and report generation for CrisisBridge."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class DisasterIntent:
    domain: str
    label: str
    matched_terms: tuple[str, ...]


DOMAIN_TERMS: dict[str, tuple[str, ...]] = {
    "flood": ("flood", "flooding", "baadh", "inundation", "waterlogging", "river overflow"),
    "earthquake": ("earthquake", "seismic", "tremor", "bhukamp"),
    "cyclone": ("cyclone", "hurricane", "typhoon", "storm surge", "toofan"),
    "fire": ("wildfire", "forest fire", "active fire", "bushfire", "aag"),
    "landslide": ("landslide", "mudslide", "rockfall", "land slide"),
    "drought": ("drought", "dry spell", "water scarcity", "sukha"),
    "heat": ("heatwave", "heat wave", "extreme heat", "loo"),
    "conflict": ("war", "conflict", "violence", "attack", "battle"),
    "health": ("outbreak", "epidemic", "pandemic", "disease", "health emergency"),
}


def classify_disaster_question(question: str) -> DisasterIntent:
    lowered = question.casefold()
    matches: list[tuple[int, str, str]] = []
    for domain, terms in DOMAIN_TERMS.items():
        for term in terms:
            if term in lowered:
                matches.append((len(term), domain, term))
    if not matches:
        return DisasterIntent("general", "world issue", ())
    matches.sort(reverse=True)
    domain = matches[0][1]
    terms = tuple(term for _, found_domain, term in matches if found_domain == domain)
    return DisasterIntent(domain, domain.replace("_", " "), terms)


def _value(value: object, fallback: str = "Not reported by the connected source") -> str:
    if value is None or str(value).strip() in {"", "nan", "NaN", "None"}:
        return fallback
    return str(value)


def render_disaster_report(
    question: str,
    intent: DisasterIntent,
    *,
    location: str | None = None,
    status: str | None = None,
    event_time: str | None = None,
    affected_people: object = None,
    deaths: object = None,
    injuries: object = None,
    missing_people: object = None,
    affected_areas: Iterable[str] | None = None,
    resources: Iterable[str] | None = None,
    responders: Iterable[str] | None = None,
    source_links: Iterable[tuple[str, str]] | None = None,
    evidence_status: str = "Prototype routing; verify with an authoritative live source",
    confidence: str = "Low until a current source record is attached",
    limitations: str = "Unknown values are not treated as zero. Casualties must be explicitly reported by a source.",
) -> str:
    """Build a long-form Markdown report while preserving unknowns and provenance."""
    areas = ", ".join(affected_areas or []) or "Not reported by the connected source"
    needs = ", ".join(resources or []) or "Assess water, food, medicine, shelter, rescue, and communications needs"
    people = ", ".join(responders or []) or "Not reported by the connected source"
    links = " · ".join(f"[{name}]({url})" for name, url in (source_links or []))
    if not links:
        links = "No source link attached yet"

    return f"""### {intent.label.title()} situation report

**Question received:** {question}

**Direct status:** {_value(status, 'Not confirmed by the connected source')}

| Field | Report |
|---|---|
| Problem type | {intent.label.title()} |
| Location | {_value(location)} |
| Event or report time | {_value(event_time)} |
| Affected people | {_value(affected_people)} |
| Deaths | {_value(deaths)} |
| Injuries | {_value(injuries)} |
| Missing people | {_value(missing_people)} |
| Affected areas | {areas} |
| Evidence status | {evidence_status} |
| Confidence | {confidence} |

**What may be happening:** The agent has identified this as a {intent.label} question. It should combine hazard observations, official warnings, humanitarian reports, and impact assessments rather than relying on a single severity score.

**Who may need help:** {needs}.

**Who may be responding:** {people}.

**Casualty rule:** Death and injury figures are shown only when an attached source explicitly reports them. The agent must not infer deaths from magnitude, rainfall, population, media attention, or a generic risk label.

**Recommended response workflow:** Confirm the exact city, district, block, or village; check the newest official bulletin; compare affected-population and casualty figures across sources; identify verified shelters and responders; and record the last retrieval time before taking action.

**Sources:** {links}

**Limitations:** {limitations}
"""


def supported_prompt() -> str:
    return (
        "Ask about any flood, earthquake, cyclone, wildfire, landslide, drought, heatwave, "
        "conflict, health emergency, affected people, deaths, resources, responders, or exact location."
    )
