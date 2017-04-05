import falcon
import redis
import os
from pprint import pformat
from common.utils import oceanus_logging, is_internal_ip
from common.settings import (OCEANUS_SITES,
                             REDIS_HOST,
                             REDIS_PORT)
from common.gopub_utils import is_available_gopub
logger = oceanus_logging()

CHUNK_NUM_SUM = sum([i["chunk_num"] for i in OCEANUS_SITES])
REDIS_DELAY_LIMIT_RATE = int(os.environ.get('REDIS_DELAY_LIMIT_RATE', 2))
REDIS_DELAY_LIMIT = CHUNK_NUM_SUM * REDIS_DELAY_LIMIT_RATE


class HealthCheckResource(object):

    def __init__(self):
        self.r = None
        self.r_info = None

    def _connect_redis(self):
        try:
            self.r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)
            self.r_info = self.r.info()
        except Exception as e:
            logger.critical('Problem Connecting Redis. {}'.format(e))
            return False

        return True

    def _create_error_resp(self, resp, body=None):
        resp.status = falcon.HTTP_503
        if not resp.body:
            resp.body = ''
        if not body:
            body = resp.body + "503 server error"
        resp.body = resp.body + body
        logger.critical('{}'.format(resp.body))
        return resp

    def _create_success_resp(self, resp, body=None):
        resp.status = falcon.HTTP_200
        if not resp.body:
            resp.body = ''
        if not body:
            body = resp.body + "ok\n"
        resp.body = resp.body + body
        return resp

    def _get_client_rad(self, access_route):
        """In most cases, the client's IP and
        load balancer's IP are returned.
        But rarely contains the user side of proxy IP,
        return three IP in access_route

        access_route
        e.g.
        [*.*.*.*] is example of real clieant ip.

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

    def on_get(self, req, resp):
        r_result = self._connect_redis()
        if not r_result:
            resp = self._create_error_resp(resp)
            return

        if not is_available_gopub():
            resp = self._create_error_resp(resp)
            return

        resp = self._create_success_resp(resp)
        return


class RedisStatusResource(HealthCheckResource):

    def on_get(self, req, resp):
        logger.debug("CHUNK_NUM_SUM:{}".format(CHUNK_NUM_SUM))
        logger.debug("REDIS_DELAY_LIMIT:{}".format(REDIS_DELAY_LIMIT))
        r_result = self._connect_redis()
        if not r_result:
            resp = self._create_error_resp(resp)
            return

        r_keys = self.r.keys("*")
        lists = {}
        total = 0
        for key in r_keys:
            key = key.decode('utf-8')
            key_type = self.r.type(key).decode('utf-8')
            logger.debug("key:{} key_type:{}".format(key, key_type))
            if key_type in ("list", "set"):
                lists[key] = self.r.llen(key)
                total = total + self.r.llen(key)

        client_ip = self._get_client_rad(req.access_route)
        if req.get_param('debug', required=False):
            if is_internal_ip(client_ip):
                info = ("Redis status\n\n"
                        "lists: {}\n"
                        "total/limit: {}/{}\n"
                        "Redis info : {}").format(lists,
                                                  total, REDIS_DELAY_LIMIT,
                                                  pformat(self.r_info))
            else:
                info = ("Your ip {} "
                        "is not included "
                        "in the internal_ips".format(client_ip))

            resp = self._create_success_resp(resp, body=info)

        elif total > REDIS_DELAY_LIMIT:
            log_body = ("over deley_limit!\n"
                        "lists: {}\n"
                        "total/limit:"
                        "{}/{}".format(lists,
                                       total,
                                       REDIS_DELAY_LIMIT))
            resp = self._create_error_resp(resp, body=log_body)
        else:
            info = "ok"
            resp = self._create_success_resp(resp, body=info)
