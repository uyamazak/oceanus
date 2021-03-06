import json
import redis
import falcon
import ipaddress
from user_agents import parse as parse_ua
from timeout_decorator import timeout
from common.settings import REDIS_HOST, REDIS_PORT, OCEANUS_SITES
from common.utils import oceanus_logging, get_client_rad
from common.errors import RedisWritingError
logger = oceanus_logging()
TIMEOUT_SECONDS = 3


class ExecutionResource(object):
    """
    Execution is oceanus arm's base Class.
    So you can not use this class directly.
    Default GET and POST is disabled.

    After receiving data with POST or GET and validation,
    if there is no error, save it in Redis in json format.

    For quick response, save to Redis,
    instead BigQuery direct.
    """

    def __init__(self):
        self.r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)

    @timeout(TIMEOUT_SECONDS)
    def write_to_redis(self, site_name, data):
        result = None
        try:
            result = self.r.lpush(site_name, data)

        except Exception as e:
            logger.critical('Problem adding data to Redis. {}'.format(e))
            logger.critical('losting data:{}'.format(data))
            raise RedisWritingError

        return result

    @timeout(TIMEOUT_SECONDS)
    def publish_to_redis(self, site_name, data):
        redis_publish_result = None
        try:
            redis_publish_result = self.r.publish(site_name, data)
        except Exception as e:
            logger.error('Problem publish to Redis. '
                         '{} {}'.format(e, redis_publish_result))

        return redis_publish_result

    def validate_json(self, field, value, error):
        if not value:
            return
        try:
            json.loads(value)
        except Exception as e:
            logger.error('json.loads error:{}'.format(e))
            error(field, 'Must be valid JSON')

    def validate_ip(self, field, value, error):
        if not value:
            return
        try:
            ip_obj = ipaddress.ip_address(value)
        except ValueError as e:
            logger.error('ipaddress error:{}'.format(e))
            error(field, 'Must be valid IP')
            return

        if ip_obj.version == 6:
            logger.info("used IPv6 {}".format(value))

        if not (ip_obj.is_global or ip_obj.is_private):
            message = 'ip not global or private:{}'.format(value)
            logger.error(message)
            error(field, message)

    def clean_json(self, json_text):
        if not json_text:
            return
        json_text = json.loads(json_text)
        json_text = json.dumps(json_text, sort_keys=True, separators=(',', ':'))
        return json_text

    def adjust_user_data(self, user_data):
        return user_data

    def get_client_rad(self, access_route):
        return get_client_rad(access_route, logger)

    def get_client_device(self, ua) -> str:
        device = ""

        if not ua:
            return device
        try:
            parse_result = parse_ua(ua)
        except Exception as e:
            logger.warning("parse_ua error: {}".format(e))
            return device

        if parse_result.is_pc:
            device = "pc"
        elif parse_result.is_mobile:
            device = "mobile"
        elif parse_result.is_tablet:
            device = "tablet"
        elif parse_result.is_bot:
            device = "bot"

        return device

    def get_default_site_name(self, method_label):
        "return first site_name from OCEANUS_SITES"
        sites = [site["site_name"] for site in OCEANUS_SITES
                 if site["method"] == method_label]
        try:
            return sites[0]
        except IndexError:
            logger.error("method {} "
                         "site not found".format(method_label))
            raise

    def site_exists(self, site_name, method_label):
        return site_name in \
            [site["site_name"] for site in OCEANUS_SITES
             if site["method"] == method_label]

    """
    Default both method is disabled.
    Use overwrite them
    """

    def on_get(self, req, resp, site_name):
            resp.body = "METHOD GET IS INVALID"
            resp.status = falcon.HTTP_400

    def on_post(self, req, resp, site_name):
            resp.body = "METHOD GET IS INVALID"
            resp.status = falcon.HTTP_400
