import json
from common.utils import oceanus_logging, convert2jst
logger = oceanus_logging()

TASK_KEY_PREFIX = "task_revelation_"
TASK_KEY_EXPIRE = 300
TASK_KEY_LIMIT = 30


class BaseHook():

    def prepare_item(self, message):
        channel = message['channel'].decode('utf-8')
        data = json.loads(message["data"].decode('utf-8'), encoding="utf-8")
        dt = None
        if data["dt"]:
            dt = convert2jst(data["dt"])
        jsn = None
        if data["jsn"]:
            jsn = json.loads(data["jsn"])
        return {"data":    data,
                "channel": channel,
                "dt":      dt,
                "jsn":     jsn,
                }

    def is_registerable_task(self, task_id):
        key = "{}{}".format(TASK_KEY_PREFIX, task_id)

        if self.redis.get(key):
            logger.error("task {} already registerd.".format(key))
            return False

        exists_task_count = len(self.redis.keys(TASK_KEY_PREFIX + "*"))
        logger.debug("exists_task_count: {}".format(exists_task_count))
        if exists_task_count > TASK_KEY_LIMIT:
            logger.error("task num is over limit")
            return False

        result = self.redis.setex(key, TASK_KEY_EXPIRE, 1)
        return result

    def __init__(self, message, redis):
        self.item = self.prepare_item(message)
        self.redis = redis

    def main(self) -> int:
        """main() must return executed count"""
        return 0
