# oceanus common settings
# This file is because it is used for both A and B,
# and to recommend the use of a hard link .
# When you git clone from repository,
# please create a hard link to run the init.sh.

from os import environ


""" Redis settings"""
REDIS_HOST = environ.get('REDIS_PD_SERVICE_HOST', "localhost")
REDIS_PORT = int(environ.get('REDIS_PD_SERVICE_PORT', 6379))

""" RabbitMQ settings"""
RABBITMQ_HOST = environ.get('RABBITMQ_SERVICE_HOST', 'localhost')
RABBITMQ_PORT = int(environ.get('RABBITMQ_SERVICE_PORT', 5672))
RABBITMQ_USER = environ.get('RABBITMQ_USER', 'guest')
RABBITMQ_PASSWORD = environ.get('RABBITMQ_PASSWORD', 'guest')

""" SendGrid settings"""
SENDGRID_API_KEY = environ.get('SENDGRID_API_KEY', "")
SENDGRID_FROM_EMAIL = environ.get('SENDGRID_FROM_EMAIL', "yu_yamazaki+sgfrom@bizocean.co.jp")
SENDGRID_TO_EMAIL = environ.get('SENDGRID_TO_EMAIL', "yu_yamazaki+sgto@bizocean.co.jp")

"""
BigQuery's table settings
"""
LOG_TABLE_SCHEMA = [
    {'name': 'dt',  'type': 'STRING', 'mode': 'REQUIRED',
     'description': 'datetime with micro seconds'},
    {'name': 'oid', 'type': 'STRING', 'mode': 'REQUIRED',
     'description': 'option id or oceanus id'},
    {'name': 'sid', 'type': 'STRING', 'mode': 'REQUIRED',
     'description': 'session id'},
    {'name': 'uid', 'type': 'STRING', 'mode': 'nullable',
     'description': 'user id'},
    {'name': 'rad', 'type': 'STRING', 'mode': 'REQUIRED',
     'description': 'remote address, ip'},
    {'name': 'evt', 'type': 'STRING', 'mode': 'REQUIRED',
     'description': 'event name'},
    {'name': 'tit', 'type': 'STRING', 'mode': 'nullable',
     'description': 'title, page title etc'},
    {'name': 'url', 'type': 'STRING', 'mode': 'nullable',
     'description': 'url'},
    {'name': 'ref', 'type': 'STRING', 'mode': 'nullable',
     'description': 'referer'},
    {'name': 'jsn', 'type': 'STRING', 'mode': 'nullable',
     'description': 'json format text'},
    {'name': 'ua',  'type': 'STRING', 'mode': 'nullable',
     'description': 'user agent'},
    {'name': 'dev', 'type': 'STRING', 'mode': 'nullable',
     'description': 'device detected by ua'},
    {'name': 'enc', 'type': 'STRING', 'mode': 'nullable',
     'description': 'encode'},
    {'name': 'scr', 'type': 'STRING', 'mode': 'nullable',
     'description': 'screen size'},
    {'name': 'vie', 'type': 'STRING', 'mode': 'nullable',
     'description': 'view size'},
]

FORM_TABLE_SCHEMA = [
    {'name': 'dt',    'type': 'STRING', 'mode': 'REQUIRED'},
    {'name': 'oid',   'type': 'STRING', 'mode': 'REQUIRED'},
    {'name': 'sid',   'type': 'STRING', 'mode': 'REQUIRED'},
    {'name': 'rad',   'type': 'STRING', 'mode': 'REQUIRED'},
    {'name': 'uid',   'type': 'STRING', 'mode': 'nullable'},
    {'name': 'name',  'type': 'STRING', 'mode': 'nullable'},
    {'name': 'cname', 'type': 'STRING', 'mode': 'nullable'},
    {'name': 'email', 'type': 'STRING', 'mode': 'nullable'},
    {'name': 'tel',   'type': 'STRING', 'mode': 'nullable'},
    {'name': 'jsn',   'type': 'STRING', 'mode': 'nullable'},
    {'name': 'ua',    'type': 'STRING', 'mode': 'nullable'},
    {'name': 'dev',   'type': 'STRING', 'mode': 'nullable'},
    {'name': 'url',   'type': 'STRING', 'mode': 'nullable'},
    {'name': 'enc',   'type': 'STRING', 'mode': 'nullable'},
]

"""
'OCEANUS_SITES' is list of dictionaries
 that contains several parameters

'site_name' used as
 - redis list's key name,
 - part of BigQuery table name,
 - url path (/swallow/bizocean)
   default: fisrt one
'table_schema' table schema of BigQuery
'method' method_name in SwallowResorce or PirateResource
'chunk_num'
 When writing to the BigQuery, divided into small chunks
 1 is every time, default 50

e.g.
(
    {"site_name": (string),
     "table_schema": (dict),
     "method": (string),
     "chunk_num": (int)
     },
)
"""

OCEANUS_SITES = (
    {"site_name": "bizocean",
     "table_schema": LOG_TABLE_SCHEMA,
     "method": 'swallow',
     "chunk_num": 50,
     },
    {"site_name": "skj",
     "table_schema": LOG_TABLE_SCHEMA,
     "method": 'swallow',
     "chunk_num": 25,
     },
    {"site_name": "bizpow",
     "table_schema": LOG_TABLE_SCHEMA,
     "method": 'swallow',
     "chunk_num": 25,
     },
    {"site_name": "moneynext",
     "table_schema": LOG_TABLE_SCHEMA,
     "method": 'swallow',
     "chunk_num": 25,
     },
    {"site_name": "movieform",
     "table_schema": FORM_TABLE_SCHEMA,
     "method": 'pirate',
     "chunk_num": 1,
     },
    {"site_name": "namecard",
     "table_schema": FORM_TABLE_SCHEMA,
     "method": 'pirate',
     "chunk_num": 1,
     },
)
