import falcon
import redis
import os

REDIS_HOST = os.environ['REDISMASTER_SERVICE_HOST']
REDIS_PORT = os.environ['REDISMASTER_SERVICE_PORT']
REDIS_LIST = os.environ['REDISLIST']

class HelthCheckResource(object):
    def on_get(self, req, resp):
        try:
            r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)
            r.info()
        except Exception as e:
            resp.status = falcon.HTTP_503
            resp.body = 'fail connecting redis'
            return

        resp.status = falcon.HTTP_200
        resp.body = 'ok'
