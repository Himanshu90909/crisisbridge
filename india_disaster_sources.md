# Verified India disaster sources

## NDMA SACHET
Official NDMA SACHET describes itself as an authorized, pan-India, multi-hazard alert portal using CAP and geo-targeted warnings. It lists alert-generating agencies including NDMA, IMD, CWC, INCOIS, FSI, and DGRE, and provides an India CAP RSS feed plus location-specific weather and alerts. Official pages: https://sachet.ndma.gov.in/ and https://sachet.ndma.gov.in/CapFeed. The RSS page links the agency integration guide at https://sachet.ndma.gov.in/docs/Integration_Guide_For_Agencies.pdf.

## IMD
The official IMD API reference documents city and latitude/longitude forecasts, current weather, district and station nowcasts, district/subdivision warnings, district/state rainfall, river-basin QPF, cyclone track/wind/cone, radar/lightning, marine bulletins, and highway warnings. Reference: https://api.imd.gov.in/public/api_reference.html.

## NDMA GIS
The official ArcGIS REST directory is publicly available at https://gis-dm.ndma.gov.in/server/rest/services. It exposes India and state folders, ActiveCase, Disaster_Alert, MultiHazard, Assam, flood-related and other services, but each service must be inspected before production use for schema, licensing, and freshness.

## Evidence policy
SACHET and IMD should be treated as primary official warning/weather sources. NDMA GIS should provide geospatial layers. News and social signals should be secondary corroboration, never independent disaster counts. The event engine must deduplicate reports referring to the same event and preserve source URLs, timestamps, agency, freshness, confidence, and explicit casualty fields. Missing deaths or affected-person counts must remain `Not reported`; the system must not infer them from severity, headlines, or population data.
