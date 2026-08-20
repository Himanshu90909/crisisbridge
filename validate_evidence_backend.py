from evidence_store import make_event_key, new_record, retrieve
from india_sources import SACHET_URL, IMD_API_REFERENCE, NDMA_GIS_URL
r = new_record(domain='flood', title='SACHET Flood alert', summary='Flood alert for Assam', location='Assam', country='India', source_name='NDMA SACHET', source_url=SACHET_URL, source_tier='primary-government', observed_at='2026-08-20T00:00:00Z')
assert make_event_key('flood', 'SACHET Flood alert', 'Assam') == r.event_key
assert retrieve('Assam flood', [r]) == [r]
assert IMD_API_REFERENCE.startswith('https://') and NDMA_GIS_URL.startswith('https://')
print('evidence_backend_validation_ok')
