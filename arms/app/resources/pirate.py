import falcon
import json
from cerberus import Validator
from datetime import datetime
from common.gopub_utils import publish2gopub
from common.errors import RedisWritingError
from common.utils import oceanus_logging
from resources.execution import ExecutionResource

logger = oceanus_logging()


class PirateResource(ExecutionResource):
    method_label = "pirate"
    """
    Pirate receives POST data.
    From HTML form, AJAX etc.
    Response empty string.
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
            logger.info('cut ua {}:{}'.format(ua_max, user_data['ua']))

        return user_data

    def on_post(self, req, resp, site_name):
        if not site_name:
            site_name = self.get_default_site_name(self.method_label)
            logger.debug("use defaule site_name "
                         "{} {}".format(site_name, self.method_label))
        if not self.site_exists(site_name, self.method_label):
            resp.status = falcon.HTTP_404
            message = 'site name not found:{0}'.format(site_name)
            resp.body = message
            logger.error(message)
            return
        logger.debug("{}".format(req.query_string))
        resp.set_header('Access-Control-Allow-Origin', '*')
        # resp.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        # resp.set_header('Access-Control-Allow-Headers', '*')
        # resp.set_header('X-Content-Type-Options', 'nosniff')
        resp.content_type = 'text/plain; charset=UTF-8'
        """
        item_dict = { key: (
                            user_data,
                            validate_schema
                           ),
                    }
        key is BigQuery's column name
        """
        client_rad = self.get_client_rad(req.access_route)
        item_dict = {
            'dt':  (str(datetime.utcnow()),
                    {'type': 'string'}
                    ),
            'sid': (req.get_param('sid', required=True),
                    {'type': 'string',
                     'regex': '^[0-9a-f]{1,32}$'}
                    ),
            'uid': (req.get_param('uid', required=False, default=""),
                    {'type': 'string',
                     'nullable': True,
                     'empty': True,
                     'maxlength': 64}
                    ),
            'oid': (req.get_param('oid', required=False, default=""),
                    {'type': 'string',
                     'maxlength': 16}
                    ),
            'rad': (client_rad,
                    {'validator': self.validate_ip}
                    ),
            'ua':  (req.user_agent,
                    {'type': 'string',
                     'nullable': True,
                     'empty': True,
                     'maxlength': 512}
                    ),
            'dev': (self. get_client_device(req.user_agent),
                    {'type': 'string',
                     'nullable': True,
                     'empty': True,
                     'maxlength': 16}
                    ),
            'url':  (req.get_param('url', required=False),
                     {'type': 'string',
                      'nullable': True,
                      'empty': True,
                      'maxlength': 1024},
                     ),
            # user name
            'name': (req.get_param('name',  required=False),
                     {'type': 'string',
                      'nullable': True,
                      'empty': True,
                      'maxlength': 1024},
                     ),
            # company name
            'cname': (req.get_param('cname', required=False),
                      {'type': 'string',
                       'nullable': True,
                       'empty': True,
                       'maxlength': 1024},
                      ),
            'email': (req.get_param('email', required=False),
                      {'type': 'string',
                       'nullable': True,
                       'empty': True,
                       'maxlength': 1024},
                      ),
            'tel':  (req.get_param('tel',   required=False),
                     {'type': 'string',
                      'nullable': True,
                      'empty': True,
                      'maxlength': 1024},
                     ),
            'jsn': (req.get_param('jsn',  required=False),
                    {'validator': self.validate_json,
                     'nullable': True,
                     'empty': True,
                     'maxlength': 10000},
                    ),
            'enc': (req.get_param('enc',  required=False, default=""),
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
            if req.get_param('debug', required=False):
                resp.body = "{}".format(v.errors)
                logger.error(resp.body)
            resp.status = falcon.HTTP_400
            return

        user_data['jsn'] = self.clean_json(user_data['jsn'])
        redis_data = json.dumps(user_data, sort_keys=True, separators=(',', ':'))
        redis_result = None
        try:
            redis_result = self.write_to_redis(site_name, redis_data)
        except RedisWritingError:
            resp.status = falcon.HTTP_500

        try:
            publish2gopub(site_name, redis_data)
        except Exception as e:
            logger.error("gopub failed:{}".format(e))

        if req.get_param('debug', required=False):
            logger.info("site_name:{}\n"
                        "user_data:{}\n"
                        "validate errors:{}\n"
                        "redis result: \n"
                        "".format(site_name,
                                  user_data,
                                  v.errors,
                                  redis_result))
        else:
            resp.body = ""
