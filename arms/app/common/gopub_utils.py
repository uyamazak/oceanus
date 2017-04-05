# Since this file is called from several applications,
# I recommend sharing it with a hard link
# When you git clone from repository,
# please create a hard link to run the management/link_common_files.sh.
from os import environ
from socket import socket, AF_INET, SOCK_STREAM
from common.settings import GOPUB_HOST, GOPUB_PORT
from common.utils import oceanus_logging
logger = oceanus_logging()

GOPUB_BUFFER_SIZE = int(environ.get("GOPUB_BUFFER_SIZE", 4096))
GOPUB_TIMEOUT = float(environ.get("GOPUB_TIMEOUT", 0.02))


def publish2gopub(site_name: str, data: str) -> bool:
    client = socket(AF_INET, SOCK_STREAM)
    client.settimeout(GOPUB_TIMEOUT)
    logger.debug("site_name:{}".format(site_name))
    try:
        client.connect((GOPUB_HOST, GOPUB_PORT))
        send_data = '{} {}'.format(site_name, data).encode("utf-8")
        # logger.debug(send_data)
        client.send(send_data)
        response = client.recv(GOPUB_BUFFER_SIZE)
    except Exception as e:
        logger.error("socket error: {}".format(e))
        client.close()
        return False

    client.close()
    if send_data != response:
        logger.error("The sent data is not equal to the returned data. \n"
                     "send_data:{}\n"
                     "response:{}".format(send_data, response))
        return False

    return True


def is_available_gopub() -> bool:
    client = socket(AF_INET, SOCK_STREAM)
    try:
        client.connect((GOPUB_HOST, GOPUB_PORT))
    except Exception as e:
        logger.critical('Problem Connecting GOPUB SERVER:{}'.format(e))
        return False
    else:
        return True
