# World Agent source and casualty-data policy

## Source families

CrisisBridge should answer only from source records that carry an origin, timestamp, geography, and update status. GDACS is a global disaster-awareness and coordination framework. ReliefWeb provides humanitarian reports and a disaster list. EM-DAT is a historical international disaster database. UCDP provides conflict-fatality datasets. WHO and national public-health agencies should provide outbreak and mortality data. USGS supplies earthquake event observations, NASA FIRMS supplies active-fire observations, and Open-Meteo supplies weather context.

## Casualty rules

The World Agent must never infer a death count from an event's magnitude, severity score, affected population, or media volume. It should report deaths only when a source explicitly provides a count, and it must show whether the count is confirmed, reported, estimated, cumulative, or provisional. If sources disagree, it should show a range or list the separate figures with timestamps instead of selecting an apparently precise number.

The answer schema should include: problem type, location, event time, current status, affected population, deaths, injuries, missing-person count, source, source timestamp, confidence, data limitations, and recommended verification step. Unknown values must be displayed as "Not reported by the connected source" rather than zero.

## Product domains

The first-class domain taxonomy can include disasters and hazards, climate and weather, conflict and violence, public health, food and agriculture, water, energy, economy and markets, supply chain, internet and infrastructure, cities and housing, and science and technology. Each domain needs a dedicated adapter and a provenance-aware normalized schema; it should not be treated as live merely because a placeholder card exists.

## References

- GDACS: https://gdacs.org/
- ReliefWeb API: https://reliefweb.int/help/api
- ReliefWeb disaster dataset: https://data.humdata.org/dataset/reliefweb-disasters-list
- EM-DAT: https://www.emdat.be/
- UCDP downloads: https://ucdp.uu.se/downloads/
- USGS Earthquake API: https://earthquake.usgs.gov/fdsnws/event/1/
- NASA FIRMS API: https://firms.modaps.eosdis.nasa.gov/api/
- Open-Meteo: https://open-meteo.com/en/docs
- Nominatim: https://nominatim.org/release-docs/latest/api/Search/
