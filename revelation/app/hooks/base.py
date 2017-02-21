import json
from common.utils import oceanus_logging, convert2jst
logger = oceanus_logging()

TASK_KEY_PREFIX = "task_reve_"
TASK_KEY_EXPIRE = 60
TASK_KEY_LIMIT = 6

IP_KEY_PREFIX = "ip_reve_"
IP_KEY_EXPIRE = 60
IP_KEY_LIMIT = 6


class BaseHook:
    """
    this is base, so just receive message and
    redis client but do nothing.
    main() must return executed tasks count
    """

    def prepare_item(self, message) -> dict:
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

    def is_existing_key(self, key) -> bool:
        if self.redis.get(key):
            logger.error("key {} already registerd.".format(key))
            return True

        return False

    def is_over_keys_limit(self, key_search, limit) -> bool:
        count = len(self.redis.keys(key_search))
        logger.debug("key_search:{} count:{}/{}".format(key_search, count, limit))
        if count > limit:
            logger.error("{} is over limit."
                         "count:{}/{}".format(key_search,
                                              count, limit))
            return True

        return False

    def is_registerable_task(self, task_id: str) -> bool:
        """
        single task
        only 1 task in TASK_KEY_EXPIRE seconds
        """
        key = TASK_KEY_PREFIX + task_id
        if self.is_existing_key(key):
            return False
        self.redis.setex(key, TASK_KEY_EXPIRE, 1)

        """
        all tasks
        less than TASK_KEY_LIMIT in TASK_KEY_EXPIRE seconds
        """
        key_search = TASK_KEY_PREFIX + "*"
        if self.is_over_keys_limit(key_search, TASK_KEY_LIMIT):
            return False

        return True

    def is_allowed_by_ip(self, ip: str) -> bool:
        key = IP_KEY_PREFIX + ip
        count = self.redis.get(key)
        if not count:
            result = self.redis.setex(key, IP_KEY_EXPIRE, 1)
            logger.debug("key:{} count:{} "
                         "setex:{}".format(key, count, result))
            return True

        logger.debug("key:{}, count:{}".format(key, count))
        count = self.redis.incrby(key, 1)
        if count > IP_KEY_LIMIT:
            return False

        return True

    def __init__(self, message, redis):
        self.item = self.prepare_item(message)
        self.redis = redis

    def main(self) -> int:
        """
        do somethings
        """
        return 0
