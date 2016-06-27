import falcon
import os
import json
import redis
import base64
import logging
from pprint import pprint, pformat
from cerberus import Validator
from datetime import datetime
from logging import getLogger

LOG_LEVEL = os.environ['LOG_LEVEL']
logger = getLogger(__name__)
handler = logging.StreamHandler()
logger.setLevel(getattr(logging, LOG_LEVEL))
logger.addHandler(handler)

REDIS_HOST = os.environ['REDISMASTER_SERVICE_HOST']
REDIS_PORT = os.environ['REDISMASTER_SERVICE_PORT']
REDIS_LIST = os.environ['REDISLIST']


class SwallowResource(object):

    r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)
    redis_errors = 0

    def write_to_redis(self, data):
        try:
            result = self.r.lpush(REDIS_LIST, data)
        except Exception as e:
            logger.critical('Problem adding data to Redis. {0}'.format(e))
            self.redis_errors += 1

        return result

    def validate_json(self, field, value, error):
        if not value:
            return
        try:
            json.loads(value)
        except:
            error(field, 'Must be valid JSON')

    def clean_json(self, json_text):
        if not json_text:
            return
        json_text = json.loads(json_text)
        json_text = json.dumps(json_text, sort_keys=True)
        return json_text

    def adjust_user_data(self, user_data):
        user_data['enc'] = user_data['enc'].upper()
        if len(user_data['ua']) > 256:
            user_data['ua'] = user_data['ua'][0:256]
            logger.info('cut ua 256:{0}'.format(user_data['ua']) )

        return user_data

    def on_get(self, req, resp):

        resp.set_header('Access-Control-Allow-Origin', '*')

        # for load balancer
        rad = req.access_route[0]
        user_data = {
            # date and time
            'dt': str(datetime.utcnow()),
            # client id in user cookie
            'sid': req.get_param('sid', required=True),
            # remote address ip
            'rad': rad,
            # event name
            'evt': req.get_param('evt', required=True),
            # user agent
            'ua': req.user_agent,
            # oceanus id
            'oid': req.get_param('oid', required=True),
            # user uniq id ex. bizocean id
            'uid': req.get_param('uid', required=False),
            # encode
            'enc': req.get_param('enc', required=True),
            'url': req.get_param('url', required=True),
            # referer
            'ref': req.get_param('ref', required=False),
            # urlencoded json text
            'jsn': req.get_param('jsn', required=False),
            # page title
            'tit': req.get_param('tit', required=False),
            # screen size
            'scr': req.get_param('scr', required=False),
            # view size
            'vie': req.get_param('vie', required=False),
        }

        validate_schema = {
            'dt': {'type': 'string'},
            'oid': {'type': 'string',
                    'maxlength': 16},
            'sid': {'type': 'string',
                    'regex': '^[0-9a-f]{16,32}$'},
            'uid': {'type': 'string',
                    'nullable': True,
                    'empty': True,
                    'maxlength': 64},
            'rad': {'type': 'string',
                    'regex': '^(([1-9]?[0-9]|1[0-9]{2}|'
                             '2[0-4][0-9]|25[0-5])\.){3}'
                             '([1-9]?[0-9]|1[0-9]{2}|'
                             '2[0-4][0-9]|25[0-5])$'},
            'evt': {'type': 'string', 'maxlength': 16},
            'tit': {'type': 'string',
                    'nullable': True, 'empty': True, 'maxlength': 256},
            'url': {'type': 'string',
                    'nullable': True, 'empty': True, 'maxlength': 1024},
            'ref': {'type': 'string',
                    'nullable': True, 'empty': True, 'maxlength': 1024},
            'jsn': {'validator': self.validate_json,
                    'nullable': True, 'empty': True, 'maxlength': 1024},
            'ua': {'type': 'string',
                   'nullable': True, 'empty': True, 'maxlength': 256},
            'enc': {'type': 'string',
                    'empty': True,
                    'regex': '^[0-9a-zA-Z\-(\)_\s]+$',
                    'maxlength': 16},
            'scr': {'type': 'string',
                    'nullable': True, 'empty': True, 'maxlength': 16},
            'vie': {'type': 'string',
                    'nullable': True, 'empty': True, 'maxlength': 16},
        }

        user_data = self.adjust_user_data(user_data)
        v = Validator(validate_schema)
        validate_result = v.validate(user_data)

        redis_result = False
        if validate_result:
            user_data['jsn'] = self.clean_json(user_data['jsn'])
            resp.status = falcon.HTTP_200
            redis_data = json.dumps(user_data)
            redis_result = self.write_to_redis(redis_data)
        else:
            logger.error("validate error:{0} {1}".format(v.errors, user_data))
            resp.status = falcon.HTTP_400

        if req.get_param('debug', required=False):
            resp.body = "oceanus swallow debug" \
                         + "\n\n user_data:\n" + pformat(user_data) \
                         + '\n\n validate: ' + pformat(validate_result) \
                         + '\n\n validate errors:\n' + pformat(v.errors) \
                         + '\n\n access_route: ' + pformat(req.access_route) \
                         + '\n\n context:\n' + pformat(req.context) \
                         + '\n\n headers:\n' + pformat(req.headers) \
                         + '\n\n env:\n' + pformat(req.env) \
                         + '\n\n redis result: ' + pformat(redis_result)
        else:
            # response 1px gif
            resp.append_header('Cache-Control', 'no-cache')
            resp.append_header('Content-type', 'image/gif')
            resp.body = base64.b64decode('R0lGODlhAQABAGAAACH5BAEKAP'
                                         '8ALAAAAAABAAEAAAgEAP8FBAA7')

if __name__ == "__main__":
    app = falcon.API()
    swallow = SwallowResource()
    app.add_route('/swallow', swallow)
