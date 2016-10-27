from execution import ExecutionResource
import falcon
import json
from pprint import pformat
from cerberus import Validator
from datetime import datetime
from common.utils import resp_beacon_gif


class SwallowResource(ExecutionResource):

    def adjust_user_data(self, user_data):
        """
        in order to prevent unnecessary validate error
        convert lower, upper, length
        """
        if user_data['enc']:
            user_data['enc'] = user_data['enc'].upper()
        if user_data['sid']:
            user_data['sid'] = user_data['sid'].lower()
        if user_data['evt']:
            user_data['evt'] = user_data['evt'].lower()
        ua_max = 512
        if not user_data['ua']:
            user_data['ua'] = ''
        if len(user_data['ua']) > ua_max:
            user_data['ua'] = user_data['ua'][0:ua_max]
            self.logger.info('cut ua {}:{}'.format(ua_max, user_data['ua']))

        return user_data

    def on_get(self, req, resp, site_name=None):
        if site_name is None:
            site_name = 'bizocean'
        elif not self.site_exists(site_name, "swallow"):
            resp.status = falcon.HTTP_404
            message = 'site name not found:{0}'.format(site_name)
            resp.body = message
            self.logger.error(message)
            return

        resp.set_header('Access-Control-Allow-Origin', '*')

        """
        item_dict = { key: (
                            user_data,
                            validate_schema
                            ),
                    }
        key is BigQuery's column name
        """

        item_dict = {
            # date and time
            'dt': (
                   str(datetime.utcnow()),
                   {'type': 'string'}
                  ),
            # client id in user cookie
            'sid': (
                    req.get_param('sid', required=True),
                    {'type': 'string',
                     'regex': '^[0-9a-f]{1,32}$'}
                   ),
            # remote address ip
            'rad': (
                    self.get_client_rad(req.access_route),
                    {'type': 'string',
                     'regex': '^(([1-9]?[0-9]|1[0-9]{2}|'
                              '2[0-4][0-9]|25[0-5])\.){3}'
                              '([1-9]?[0-9]|1[0-9]{2}|'
                              '2[0-4][0-9]|25[0-5])$'}
                  ),
            # event name
            'evt': (
                    req.get_param('evt', required=True),
                    {'type': 'string',
                     'maxlength': 16}
                   ),
            # user agent
            'ua':  (
                    req.user_agent,
                    {'type': 'string',
                     'nullable': True,
                     'empty': True,
                     'maxlength': 512}
                    ),
            # device detecting from user agent
            'dev': (
                    self. get_client_device(req.user_agent),
                    {'type': 'string',
                     'nullable': True,
                     'empty': True,
                     'maxlength': 16}
                   ),
            # oceanus id
            'oid': (
                    req.get_param('oid', required=True),
                    {'type': 'string',
                     'maxlength': 16}
                   ),
            # user uniq id ex. bizocean id
            'uid': (
                    req.get_param('uid', required=False),
                    {'type': 'string',
                     'nullable': True,
                     'empty': True,
                     'maxlength': 64}
                    ),
            # encode
            'enc': (
                    req.get_param('enc', required=False),
                    {'type': 'string',
                     'nullable': True,
                     'empty': True,
                     'regex': '^[0-9a-zA-Z\-(\)_\s]+$',
                     'maxlength': 16}
                   ),
            'url': (
                    req.get_param('url', required=True),
                    {'type': 'string',
                     'nullable': True,
                     'empty': True,
                     'maxlength': 1024},
                   ),
            # referer
            'ref': (
                    req.get_param('ref', required=False),
                    {'type': 'string',
                     'nullable': True,
                     'empty': True,
                     'maxlength': 1024},
                   ),
            # urlencoded json text
            'jsn': (
                    req.get_param('jsn', required=False),
                    {'validator': self.validate_json,
                     'nullable': True,
                     'empty': True,
                     'maxlength': 4096}
                   ),
            # page title
            'tit': (
                    req.get_param('tit', required=False),
                    {'type': 'string',
                     'nullable': True,
                     'empty': True,
                     'maxlength': 1024}
                   ),
            # screen size
            'scr': (
                    req.get_param('scr', required=False),
                    {'type': 'string',
                     'nullable': True,
                     'empty': True,
                     'maxlength': 16}
                   ),
            # view size
            'vie': (
                    req.get_param('vie', required=False),
                    {'type': 'string',
                     'nullable': True,
                     'empty': True,
                     'maxlength': 16}
                   ),
        }
        user_data = self.adjust_user_data({k: v[0]
                                           for k, v in item_dict.items()})
        v = Validator({k: v[1]
                       for k, v in item_dict.items()})
        validate_result = v.validate(user_data)
        redis_result = False
        if validate_result:
            user_data['jsn'] = self.clean_json(user_data['jsn'])
            resp.status = falcon.HTTP_200
            redis_data = json.dumps(user_data)
            redis_result = self.write_to_redis(site_name, redis_data)
        else:
            self.logger.error("validate error:{}"
                              "user_data:{}"
                              "access_route:{}".format(v.errors,
                                                       user_data,
                                                       req.access_route))
            resp.status = falcon.HTTP_400

        if req.get_param('debug', required=False):
            resp.body = "oceanus swallow debug" \
                         + "\n\n site_name:" + site_name \
                         + "\n\n user_data:\n" + pformat(user_data) \
                         + '\n\n validate: ' + pformat(validate_result) \
                         + '\n\n validate errors:\n' + pformat(v.errors) \
                         + '\n\n access_route: ' + pformat(req.access_route) \
                         + '\n\n context:\n' + pformat(req.context) \
                         + '\n\n headers:\n' + pformat(req.headers) \
                         + '\n\n env:\n' + pformat(req.env) \
                         + '\n\n redis result: ' + pformat(redis_result) \
                         + '\n\n redis keys: ' + pformat(self.r.keys())
        else:
            # response 1px gif
            resp = resp_beacon_gif(resp)

if __name__ == "__main__":
    app = falcon.API()
    swallow = SwallowResource()
    app.add_route('/swallow', swallow)
