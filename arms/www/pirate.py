import falcon
import json
from execution import ExecutionResource
from pprint import pformat
from cerberus import Validator
from datetime import datetime


class PirateResource(ExecutionResource):
    """
    The oceanus pirate receives form data
    in JSON format, save to Redis
    """
    def adjust_user_data(self, user_data):
        """
        in order to prevent unnecessary validate error
        convert lower, upper, length
        """
        if user_data['enc']:
            user_data['enc'] = user_data['enc'].upper()
        if user_data['sid']:
            user_data['sid'] = user_data['sid'].lower()
        ua_max = 512
        if not user_data['ua']:
            user_data['ua'] = ''
        if len(user_data['ua']) > ua_max:
            user_data['ua'] = user_data['ua'][0:ua_max]
            self.logger.info('cut ua {}:{}'.format(ua_max, user_data['ua']))

        return user_data

    def on_post(self, req, resp, site_name):
        if not self.site_exists(site_name, "pirate"):
            resp.status = falcon.HTTP_404
            message = 'site name not found:{0}'.format(site_name)
            resp.body = message
            self.logger.error(message)
            return
        self.logger.debug("{}".format(req.query_string))
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
            'dt':  (
                    str(datetime.utcnow()),
                    {'type': 'string'}
                   ),
            'sid': (
                    req.get_param('sid', required=True),
                    {'type': 'string',
                     'regex': '^[0-9a-f]{1,32}$'}
                   ),
            'uid': (
                    req.get_param('uid', required=False, default=""),
                    {'type': 'string',
                     'nullable': True,
                     'empty': True,
                     'maxlength': 64}
                   ),
            'oid': (
                    req.get_param('oid', required=False, default=""),
                    {'type': 'string',
                     'maxlength': 16}
                   ),
            'rad': (
                    self.get_client_rad(req.access_route),
                    {'type': 'string',
                     'regex': '^(([1-9]?[0-9]|1[0-9]{2}|'
                              '2[0-4][0-9]|25[0-5])\.){3}'
                              '([1-9]?[0-9]|1[0-9]{2}|'
                              '2[0-4][0-9]|25[0-5])$'}
                   ),
            'ua':  (
                    req.user_agent,
                    {'type': 'string',
                     'nullable': True,
                     'empty': True,
                     'maxlength': 512}
                   ),
            'dev': (
                    self. get_client_device(req.user_agent),
                    {'type': 'string',
                     'nullable': True,
                     'empty': True,
                     'maxlength': 16}
                    ),
            'url':  (
                     req.get_param('url', required=False),
                     {'type': 'string',
                      'nullable': True,
                      'empty': True,
                      'maxlength': 1024},
                    ),
            # user name
            'name': (
                     req.get_param('name',  required=False),
                     {'type': 'string',
                      'nullable': True,
                      'empty': True,
                      'maxlength': 1024},
                    ),
            # company name
            'cname': (
                      req.get_param('cname', required=False),
                      {'type': 'string',
                       'nullable': True,
                       'empty': True,
                       'maxlength': 1024},
                     ),
            'email': (
                      req.get_param('email', required=False),
                      {'type': 'string',
                       'nullable': True,
                       'empty': True,
                       'maxlength': 1024},
                     ),
            'tel':  (
                     req.get_param('tel',   required=False),
                     {'type': 'string',
                      'nullable': True,
                      'empty': True,
                      'maxlength': 1024},
                    ),
            'jsn': (
                    req.get_param('jsn',  required=False),
                    {'validator': self.validate_json,
                     'nullable': True,
                     'empty': True,
                     'maxlength': 10000},
                   ),
            'enc': (
                    req.get_param('enc',  required=False, default=""),
                    {'type': 'string',
                     'empty': True,
                     'nullable': True,
                     'regex': '^[0-9a-zA-Z\-(\)_\s]*$',
                     'maxlength': 16}
                   )
        }
        user_data = self.adjust_user_data({k: v[0]
                                           for k, v in item_dict.items()})
        v = Validator({k: v[1] for k, v in item_dict.items()})
        validate_result = v.validate(user_data)

        if validate_result:
            resp.status = falcon.HTTP_200
        else:
            resp.status = falcon.HTTP_400
            return

        user_data['jsn'] = self.clean_json(user_data['jsn'])
        redis_data = json.dumps(user_data)
        redis_result = self.write_to_redis(site_name, redis_data)
        if not redis_result:
            self.logger.error("writing Redis failed.\n"
                              "{}\n"
                              "{}".format(redis_result, redis_data))
            resp.status = falcon.HTTP_500

        if req.get_param('debug', required=False):
            resp.body = "oceanus pirate debug" \
                        + "\n\n site_name:" + site_name \
                        + "\n\n user_data:\n" + pformat(user_data) \
                        + '\n\n validate: ' + pformat(validate_result) \
                        + '\n\n validate errors:\n' + pformat(v.errors) \
                        + '\n\n redis result: ' + pformat(redis_result) \
                        + '\n\n redis keys: ' + pformat(self.r.keys())
            return
        else:
            resp = "ok"
