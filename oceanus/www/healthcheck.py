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

        debug = req.get_param('debug', required=False)
        check_delay = req.get_param('check_delay', required=False)
        if not debug and \
           not check_delay:
            resp.status = falcon.HTTP_200
            resp.body = "ok"
            return

        r_keys = r.keys("*")
        lists = {}
        total = 0
        for key in r_keys:
            lists[key] = r.llen(key)
            total = total + r.llen(key)

        if debug:
            resp.body = ("debug\nredis:{}\ntotal:{}\n"
                         "redis_info:{}").format(lists, total,
                                                 r_info)
            return
        deley_limit = 20
        if check_delay:
            resp.body = ("check_delay\nredis:{}\n"
                         "total:{}/{}\nredis_info:{}").format(lists, total,
                                                              deley_limit,
                                                              r_info)
            if total > deley_limit:
                resp.body = "over deley_limit!\n\n" + resp.body
                resp.status = falcon.HTTP_503
