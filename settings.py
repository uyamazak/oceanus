# oceanus common settings
import os

REDIS_HOST = os.environ['REDISMASTER_SERVICE_HOST']
REDIS_PORT = os.environ['REDISMASTER_SERVICE_PORT']

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
'OCEANUS_SITES' is list of dictionaries
 contain several parameters

'site_name' used as
 - redis list's key name,
 - part of BigQuery table name,
 - url path (/swallow/bizocean)
   default bizocean
'table_schema' table schema of BigQuery
'method' swallow or pirate
'chunk_num'
 When writing to the BigQuery, divided into small chunks
 1 is every time, default 50

e.g.
(
    {"site_name": (string)},
    {"table_schema": (dict)},
    {"method": (string)},
    {"chunk_num": (int)}
)

In oceanus-redis2bq ,
the thread of the same number as the number of site starts
"""

OCEANUS_SITES = (
    {"site_name": "bizocean",
     "table_schema": LOG_TABLE_SCHEMA,
     "method": 'swallow',
     "chunk_num": 50
     },
    {"site_name": "skj",
     "table_schema": LOG_TABLE_SCHEMA,
     "method": 'swallow',
     "chunk_num": 25
     },
    {"site_name": "bizpow",
     "table_schema": LOG_TABLE_SCHEMA,
     "method": 'swallow',
     "chunk_num": 25
     },
    {"site_name": "moneynext",
     "table_schema": LOG_TABLE_SCHEMA,
     "method": 'swallow',
     "chunk_num": 25
     },
    {"site_name": "movieform",
     "table_schema": FORM_TABLE_SCHEMA,
     "method": 'pirate',
     "chunk_num": 1
     },
)
