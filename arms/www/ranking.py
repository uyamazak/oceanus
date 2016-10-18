import falcon
import redis
import os
import json
import html
from pprint import pformat
from common.utils import oceanus_logging
logger = oceanus_logging()

REDIS_HOST = os.environ['REDISMASTER_SERVICE_HOST']
REDIS_PORT = os.environ['REDISMASTER_SERVICE_PORT']


class RankingResource(object):
    def __init__(self):
        self.r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)

    def on_get(self, req, resp, name):
        ranking = self.r.zrevrange(name, 0, 100, withscores=True)
        logger.debug("ranking:{}".format(ranking))
        if not ranking:
            resp.status = falcon.HTTP_404
            resp.body = "not found {}".format(html.escape(name))
            return
        decode_ranking = [(item.decode("utf8"),score) for item, score in ranking]
        ranking_json = json.dumps(decode_ranking, indent=2, ensure_ascii=False)
        logger.info("{}".format(ranking_json))
        resp.status = falcon.HTTP_200
        resp.body = ranking_json
