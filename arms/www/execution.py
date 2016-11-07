import json
import redis
import falcon
from user_agents import parse as parse_ua
from common.settings import REDIS_HOST, REDIS_PORT, OCEANUS_SITES
from common.utils import oceanus_logging


class ExecutionResource(object):
    """
    Execution is oceanus arm's base Class.
    Gets access log, event log, and etc with json format.
    For quick response, save to redis on local network,
    instead BigQuery direct.
    """
    def __init__(self):
        self.r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)
        self.redis_errors = 0
        self.logger = oceanus_logging()

    def write_to_redis(self, site_name, data):
        result = None
        try:
            result = self.r.lpush(site_name, data)

        except Exception as e:
            self.logger.critical('Problem adding data to Redis. {0}'.format(e))
            self.redis_errors += 1

        redis_publish_result = None
        try:
            redis_publish_result = self.r.publish(site_name, data)
        except Exception as e:
            self.logger.critical('Problem publish to Redis. '
                                 '{} {}'.format(e, redis_publish_result))

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
        return user_data

    def get_client_rad(self, access_route):
        """In most cases, the client's IP and
        load balancer's IP are returned.
        But rarely contains the user side of proxy IP,
        return three IP in access_route

        access_route e.g. [*.*.*.*] is real clieant ip

        - Direct Access
          [*.*.*.*]

        - via Google Load balancer
          [*.*.*.*, 130.211.0.0/22]

        - and via client's proxy
          [002512 172.16.18.111, *.*.*.*, 130.211.0.0/22]

        """

        if len(access_route) == 3:
            """via client's proxy ip"""
            return access_route[1]
        else:
            """Direct or via Google Load balancer"""
            return access_route[0]

    def get_client_device(self, ua):
        device = ""

        if not ua:
            return device
        try:
            parse_result = parse_ua(ua)
        except Exception as e:
            self.logger.warning("parse_ua error: {}".format(e))
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

    def site_exists(self, site_name, method_label):
        sites = [site["site_name"] for site in OCEANUS_SITES
                 if site["method"] == method_label]
        if site_name in sites:
            return True
        else:
            return False

    """
    Default both method is disabled.
    """
    def on_get(self, req, resp, site_name):
            resp.body = "METHOD GET IS INVALID"
            resp.status = falcon.HTTP_400

    def on_post(self, req, resp, site_name):
            resp.body = "METHOD GET IS INVALID"
            resp.status = falcon.HTTP_400
