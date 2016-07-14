# oceanus common settings
"""
BigQuery's table schema
"""

LOG_TABLE_SCHEMA = [
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

FORM_TABLE_SCHEMA = [
    {'name': 'dt',    'type': 'STRING', 'mode': 'REQUIRED'},
    {'name': 'oid',   'type': 'STRING', 'mode': 'REQUIRED'},
    {'name': 'sid',   'type': 'STRING', 'mode': 'REQUIRED'},
    {'name': 'rad',   'type': 'STRING', 'mode': 'REQUIRED'},
    {'name': 'uid',   'type': 'STRING', 'mode': 'nullable'},
    {'name': 'name',  'type': 'STRING', 'mode': 'REQUIRED'},
    {'name': 'cname', 'type': 'STRING', 'mode': 'nullable'},
    {'name': 'email', 'type': 'STRING', 'mode': 'nullable'},
    {'name': 'tel',   'type': 'STRING', 'mode': 'nullable'},
    {'name': 'ua',    'type': 'STRING', 'mode': 'nullable'},
    {'name': 'url',   'type': 'STRING', 'mode': 'nullable'},
    {'name': 'jsn',   'type': 'STRING', 'mode': 'nullable'},
    {'name': 'enc',   'type': 'STRING', 'mode': 'nullable'},
]

"""
used as
- redis list's key name,
- part of BigQuery table name,
- url path (/swallow/bizocean)
  default bizocean
e.g.
({name}, {table schema list}, {method})
In oceanus-redis2bq ,
the thread of the same number as the number of site starts
"""

OCEANUS_SITES = (
    ("bizocean",  LOG_TABLE_SCHEMA,  'swallow'),
    ("skj",       LOG_TABLE_SCHEMA,  'swallow'),
    ("bizpow",    LOG_TABLE_SCHEMA,  'swallow'),
    ("moneynext", LOG_TABLE_SCHEMA,  'swallow'),
    ("movie",     FORM_TABLE_SCHEMA, 'pirate'),
)
