import falcon
import redis
import os
from pprint import pformat
from utils import oceanus_logging
logger = oceanus_logging()

REDIS_HOST = os.environ['REDISMASTER_SERVICE_HOST']
REDIS_PORT = os.environ['REDISMASTER_SERVICE_PORT']


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
            body = resp.body + "503 server error\n"
        resp.body = resp.body + body
        return resp

    def _create_success_resp(self, resp, body=None):
        resp.status = falcon.HTTP_200
        if not resp.body:
            resp.body = ''
        if not body:
            body = resp.body + "ok\n"
        resp.body = resp.body + body
        return resp

    def on_get(self, req, resp):
        r_result = self._connect_redis()
        if not r_result:
            resp = self._create_error_resp(resp)
            return

        resp = self._create_success_resp(resp)
        return


class RedisStatusResource(HealthCheckResource):
    def on_get(self, req, resp):
        r_result = self._connect_redis()
        if not r_result:
            resp = self._create_error_resp(resp)
            return

        r_keys = self.r.keys("*")
        lists = {}
        total = 0
        for key in r_keys:
            lists[key] = self.r.llen(key)
            total = total + self.r.llen(key)

        deley_limit = 25
        if total > deley_limit:
            resp = self._create_error_resp(resp, body="over deley_limit!\n")
            return

        info = "ok"
        if req.get_param('debug', required=False):
            info = ("Redis status\n\n"
                    "lists: {}\n"
                    "total/limit: {}/{}\n"
                    "Redis info : {}").format(lists,
                                              total, deley_limit,
                                              pformat(self.r_info))
        resp = self._create_success_resp(resp, body=info)
