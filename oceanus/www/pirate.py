import falcon
import json
import settings
import os
from pprint import pformat
from swallow import SwallowResource
from cerberus import Validator
from datetime import datetime
from utils import oceanus_logging, beacon_gif
logger = oceanus_logging()

OCEANUS_SITES = settings.OCEANUS_SITES


class PirateResource(SwallowResource):
    """
    The oceanus pirate receives form data
    in JSON format, save the BigQuery
    """

    def on_get(self, req, resp, site_name):
        if not self.site_exists(site_name, "pirate"):
            resp.status = falcon.HTTP_404
            message = 'site name not found:{0}'.format(site_name)
            resp.body = message
            logger.error(message)
            return

        resp.set_header('Access-Control-Allow-Origin', '*')
        rad = req.access_route[0]
        user_data = {
            'dt':    str(datetime.utcnow()),
            'sid':   req.get_param('sid', required=True),
            'uid':   req.get_param('uid', required=False, default=""),
            'oid':   req.get_param('oid', required=False, default=""),
            'rad':   rad,
            'ua':    req.user_agent,
            'url':   req.get_param('url', required=False),
            'name':  req.get_param('name',  required=True),
            'cname': req.get_param('cname', required=False),
            'email': req.get_param('email', required=False),
            'tel':   req.get_param('tel',   required=False),
            'jsn':   req.get_param('jsn',  required=False),
            'enc':   req.get_param('enc',  required=False, default=""),
        }
        validate_schema = {
            'dt':  {'type': 'string'},
            'oid': {'type': 'string',
                    'maxlength': 16},
            'sid': {'type': 'string',
                    'regex': '^[0-9a-f]{1,32}$'},
            'uid': {'type': 'string',
                    'nullable': True,
                    'empty': True},
            'rad': {'type': 'string',
                    'regex': '^(([1-9]?[0-9]|1[0-9]{2}|'
                    '2[0-4][0-9]|25[0-5])\.){3}'
                    '([1-9]?[0-9]|1[0-9]{2}|'
                    '2[0-4][0-9]|25[0-5])$'},
            'ua':  {'type': 'string',
                    'nullable': True, 'empty': True, 'maxlength': 512},
            'url': {'type': 'string', 'nullable': True,
                    'empty': True, 'maxlength': 1024},
            'jsn': {'validator': self.validate_json,
                    'nullable': True, 'empty': True, 'maxlength': 10000},
            'enc': {'type': 'string',
                    'empty': True,
                    'nullable': True,
                    'regex': '^[0-9a-zA-Z\-(\)_\s]*$',
                    'maxlength': 16},
            'name':  {'type': 'string', 'nullable': True,
                      'empty': True, 'maxlength': 1024},
            'cname': {'type': 'string', 'nullable': True,
                      'empty': True, 'maxlength': 1024},
            'email': {'type': 'string', 'nullable': True,
                      'empty': True, 'maxlength': 1024},
            'tel':   {'type': 'string', 'nullable': True,
                      'empty': True, 'maxlength': 1024},
        }

        user_data = self.adjust_user_data(user_data)
        v = Validator(validate_schema)
        validate_result = v.validate(user_data)

        resp.append_header('Cache-Control',
                            'no-cache, no-store, must-revalidate')
        resp.append_header('expires', 'Mon, 01 Jan 1990 00:00:00 GMT')
        resp.append_header('pragma', 'no-cache')
        resp.append_header('Content-type', 'image/gif')
        resp.body = beacon_gif()

        if not validate_result:
            resp.status = falcon.HTTP_400
            return

        user_data['jsn'] = self.clean_json(user_data['jsn'])
        redis_data = json.dumps(user_data)
        resp.status = falcon.HTTP_200
        redis_result = self.write_to_redis(redis_data, site_name)
        if not redis_result:
            resp.status = falcon.HTTP_500

        if req.get_param('debug', required=False):
            resp.body = "oceanus pirate debug" \
                        + "\n\n site_name:" + site_name \
                        + "\n\n user_data:\n" + pformat(user_data) \
                        + '\n\n validate: ' + pformat(validate_result) \
                        + '\n\n validate errors:\n' + pformat(v.errors) \
                        + '\n\n redis result: ' + pformat(redis_result) \
                        + '\n\n redis keys: ' + pformat(self.r.keys())
