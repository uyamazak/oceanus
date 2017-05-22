import falcon
import json
from pprint import pformat
from cerberus import Validator
from datetime import datetime
from resources.execution import ExecutionResource
from common.utils import oceanus_logging, is_internal_ip
from common.gopub_utils import publish2gopub
from common.errors import RedisWritingError

logger = oceanus_logging(__name__)


class PierceResource(ExecutionResource):
    """
    短縮URL用。
    サーバーからアクセスが来るので
    radやuaをGETパラメーターで受ける。
    レスポンスは1pxGifではなくokの文字列
    """
    method_label = "pierce"

    def adjust_user_data(self, user_data):
        """
        in order to prevent unnecessary validate error
        convert lower, upper, length
        """
        if user_data['enc']:
            """img tag at emailopen,
               it may contains slash for some reason."""
            user_data['enc'] = user_data['enc'].upper().replace("/", "")
        if user_data['sid']:
            user_data['sid'] = user_data['sid'].lower()
        if user_data['evt']:
            user_data['evt'] = user_data['evt'].lower()
        ua_max = 512
        if not user_data['ua']:
            user_data['ua'] = ''
        if len(user_data['ua']) > ua_max:
            user_data['ua'] = user_data['ua'][0:ua_max]
            logger.info('cut ua {}:{}'.format(ua_max, user_data['ua']))
        return user_data

    def on_get(self, req, resp, site_name=None):
        if not site_name:
            site_name = self.get_default_site_name(self.method_label)
            logger.debug("use default site_name "
                         "{} {}".format(site_name, self.method_label))

        if not self.site_exists(site_name, self.method_label):
            resp.status = falcon.HTTP_404
            message = 'site name not found:{0}'.format(site_name)
            resp.body = message
            logger.error(message)
            return

        resp.set_header('Access-Control-Allow-Origin', '*')

        """
        item_dict = { key: (
                            user_data,
                            validate_schema
                            ),
                    }
        key is used as BigQuery's column name
        """
        client_rad = self.get_client_rad(req.access_route)
        item_dict = {
            # date and time
            'dt': (str(datetime.utcnow()),
                   {'type': 'string'}
                   ),
            # client id in user cookie
            'sid': (req.get_param('sid', required=False, default=""),
                    {'type': 'string',
                     'regex': '^[0-9a-f]{0,32}$'}
                    ),
            # remote address ip
            'rad': (req.get_param('rad', required=True),
                    {'validator': self.validate_ip}
                    ),

            # event name
            'evt': (req.get_param('evt', required=True),
                    {'type': 'string',
                     'maxlength': 16}
                    ),
            # user agent
            'ua':  (req.get_param('ua', required=False, default=""),
                    {'type': 'string',
                     'nullable': True,
                     'empty': True,
                     'maxlength': 512}
                    ),
            # device detecting from user agent
            'dev': (self.get_client_device(req.get_param('ua', required=False, default="")),
                    {'type': 'string',
                     'nullable': True,
                     'empty': True,
                     'maxlength': 16}
                    ),
            # oceanus id
            'oid': (req.get_param('oid', required=True),
                    {'type': 'string',
                     'maxlength': 16}
                    ),
            # user uniq id ex. bizocean id
            'uid': (req.get_param('uid', required=False),
                    {'type': 'string',
                     'nullable': True,
                     'empty': True,
                     'maxlength': 64}
                    ),
            # encode
            'enc': (req.get_param('enc', required=False),
                    {'type': 'string',
                     'nullable': True,
                     'empty': True,
                     'regex': '^[0-9a-zA-Z\-(\)_\s]+$',
                     'maxlength': 16}
                    ),
            'url': (req.get_param('url', required=True),
                    {'type': 'string',
                     'nullable': True,
                     'empty': True,
                     'maxlength': 1024},
                    ),
            # referer
            'ref': (req.get_param('ref', required=False),
                    {'type': 'string',
                     'nullable': True,
                     'empty': True,
                     'maxlength': 1024},
                    ),
            # urlencoded json text
            'jsn': (req.get_param('jsn', required=False),
                    {'validator': self.validate_json,
                     'nullable': True,
                     'empty': True,
                     'maxlength': 4096}
                    ),
            # page title
            'tit': (req.get_param('tit', required=False),
                    {'type': 'string',
                     'nullable': True,
                     'empty': True,
                     'maxlength': 1024}
                    ),
            # screen size
            'scr': (req.get_param('scr', required=False),
                    {'type': 'string',
                     'nullable': True,
                     'empty': True,
                     'maxlength': 16}
                    ),
            # view size
            'vie': (req.get_param('vie', required=False),
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
        redis_result = None

        if validate_result:
            user_data['jsn'] = self.clean_json(user_data['jsn'])
            resp.status = falcon.HTTP_200
            redis_data = json.dumps(user_data, sort_keys=True, separators=(',', ':'))
            try:
                redis_result = self.write_to_redis(site_name, redis_data)
            except RedisWritingError:
                resp.status = falcon.HTTP_500

            try:
                publish2gopub(site_name, redis_data)
            except Exception as e:
                logger.error("gopub failed:{}".format(e))

        else:
            logger.error("validate error:{}"
                         "user_data:{}"
                         "access_route:{}".format(v.errors,
                                                  user_data,
                                                  req.access_route))
            resp.status = falcon.HTTP_400

        if req.get_param('debug', required=False) and \
           is_internal_ip(client_rad):
            resp.body = ('oceanus pierce debug'
                         '\n\n site_name:{}'
                         '\n\n user_data:\n{}'
                         '\n\n validate: {}'
                         '\n\n validate errors:\n{}'
                         '\n\n access_route: {}'
                         '\n\n context:\n{}'
                         '\n\n headers:\n{}'
                         '\n\n env:\n{}'
                         '\n\n redis result: {}'
                         '\n\n redis keys: {}'
                         ''.format(site_name,
                                   pformat(user_data),
                                   pformat(validate_result),
                                   pformat(v.errors),
                                   pformat(req.access_route),
                                   pformat(req.context),
                                   pformat(req.headers),
                                   pformat(req.env),
                                   pformat(redis_result),
                                   pformat(self.r.keys()))
                         )

        else:
            resp.body = "ok"
