# CrisisBridge global data-source findings

## Authoritative feeds

- GDACS provides global disaster awareness and coordination information and exposes event data for earthquakes, tsunamis, tropical cyclones, floods, volcanoes, droughts, and forest fires. Source: https://gdacs.org/
- ReliefWeb is a UN OCHA service with a public JSON API for humanitarian reports, disasters, updates, organizations, countries, and training. It requests an `appname` parameter, limits calls to 1,000 per day and results to 1,000 entries per call, and updates as content is added. Source: https://reliefweb.int/help/api
- HDX HAPI provides standardized humanitarian indicators from multiple sources and is designed for developers and visualizations. It is updated daily, requires an app identifier, and its coverage/freshness varies by indicator. Source: https://data.humdata.org/hapi
- USGS Earthquake Catalog provides GeoJSON queries and recommends real-time GeoJSON feeds for automated earthquake displays. Source: https://earthquake.usgs.gov/fdsnws/event/1/
- NASA FIRMS provides near-real-time active-fire detections from MODIS and VIIRS through area/country/data-availability services. Source: https://firms.modaps.eosdis.nasa.gov/api/
- Open-Meteo provides global weather forecasts and current conditions through a no-key API, including precipitation, wind, temperature, flood, and air-quality-related variables. Source: https://open-meteo.com/en/docs
- Nominatim/OpenStreetMap supports free-form and structured geocoding, reverse geocoding, village/settlement classification, and GeoJSON output. Source: https://nominatim.org/release-docs/latest/api/Search/

## Product constraints

Live feeds are not equivalent to verified ground truth. Each incident must show source, fetched time, freshness, confidence, and verification state. The interface must distinguish detected hazards, reported needs, and verified response actions. It must not expose sensitive personal data or imply that an automated score decides whose life has greater value.

## Recommended architecture

Use a full-stack application with scheduled ingestion jobs, a normalized incident schema, PostGIS-compatible geospatial storage, source adapters, caching, rate-limit handling, and a public read-only map. Keep user-submitted requests and resource-provider records behind authentication and moderation. Use a source registry so each map marker links to its original source.
