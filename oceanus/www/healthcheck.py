import falcon
import redis
import os
from pprint import pformat
from common.utils import oceanus_logging
logger = oceanus_logging()

REDIS_HOST = os.environ['REDISMASTER_SERVICE_HOST']
REDIS_PORT = os.environ['REDISMASTER_SERVICE_PORT']
REDIS_DELAY_LIMIT = int(os.environ['REDIS_DELAY_LIMIT'])


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
            key = key.decode('utf-8')
            key_type = self.r.type(key).decode('utf-8')
            logger.debug("key:{} key_type:{}".format(key, key_type))
            if key_type in ("list", "set"):
                lists[key] = self.r.llen(key)
                total = total + self.r.llen(key)

        if req.get_param('debug', required=False):
            info = ("Redis status\n\n"
                    "lists: {}\n"
                    "total/limit: {}/{}\n"
                    "Redis info : {}").format(lists,
                                              total, REDIS_DELAY_LIMIT,
                                              pformat(self.r_info))
            resp = self._create_success_resp(resp, body=info)
        elif total > REDIS_DELAY_LIMIT:
            resp = self._create_error_resp(resp, body="over deley_limit!\n")
        else:
            info = "ok"
            resp = self._create_success_resp(resp, body=info)
