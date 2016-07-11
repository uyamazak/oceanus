# oceanus common settings
"""
used as
- redis list's key name,
- part of BigQuery table name,
- url path (/swallow/bizocean)
  default bizocean

"""
OCEANUS_SITES = (
    "bizocean",
    "skj",
    "bizpow",
    "trwk",
    "aripo",
)

"""
BigQuery's table schema
"""
TABLE_SCHEMA = [
    {'name': 'dt',  'type': 'STRING', 'mode': 'REQUIRED'},
    {'name': 'oid', 'type': 'STRING', 'mode': 'REQUIRED'},
    {'name': 'sid', 'type': 'STRING', 'mode': 'REQUIRED'},
    {'name': 'uid', 'type': 'STRING', 'mode': 'nullable'},
    {'name': 'rad', 'type': 'STRING', 'mode': 'REQUIRED'},
    {'name': 'evt', 'type': 'STRING', 'mode': 'REQUIRED'},
    {'name': 'tit', 'type': 'STRING', 'mode': 'nullable'},
    {'name': 'url', 'type': 'STRING', 'mode': 'nullable'},
    {'name': 'ref', 'type': 'STRING', 'mode': 'nullable'},
    {'name': 'jsn', 'type': 'STRING', 'mode': 'nullable'},
    {'name': 'ua',  'type': 'STRING', 'mode': 'nullable'},
    {'name': 'enc', 'type': 'STRING', 'mode': 'nullable'},
    {'name': 'scr', 'type': 'STRING', 'mode': 'nullable'},
    {'name': 'vie', 'type': 'STRING', 'mode': 'nullable'},
]
