from hook.base import BaseHook
from common.gopub_utils import publish2gopub
from common.utils import oceanus_logging
logger = oceanus_logging()


class PubsubHook(BaseHook):

    def main(self) -> int:
        count = 0
        result = publish2gopub(self.message["data"])
        if result:
            count += 1

        return count
