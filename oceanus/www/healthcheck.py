import falcon
import redis
import os

REDIS_HOST = os.environ['REDISMASTER_SERVICE_HOST']
REDIS_PORT = os.environ['REDISMASTER_SERVICE_PORT']


class HelthCheckResource(object):
    def on_get(self, req, resp):
        try:
            r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)
            r_info = r.info()
        except Exception as e:
            resp.status = falcon.HTTP_503
            resp.body = 'fail connecting redis {0}'.format(e)
            return

        if req.get_param('debug', required=False):
            r_keys = r.keys("*")
            lists = {}
            total = 0
            for key in r_keys:
                lists[key] = r.llen(key)
                total = total + r.llen(key)
                resp.status = falcon.HTTP_200
                resp.body = "debug\nredis:{}\ntotal:{}".format(lists, total)
                return

        resp.status = falcon.HTTP_200
        resp.body = "ok"
