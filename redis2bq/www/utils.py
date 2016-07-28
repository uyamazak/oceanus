# This file is because it is used for both A and B,
# and to recommend the use of a hard link .
# When you git clone from repository,
# please create a hard link to run the init.sh.

import logging
import os
import base64


def oceanus_logging():
    LOG_LEVEL = os.environ['LOG_LEVEL']
    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s- '
                                  '%(levelname)s - '
                                  '%(message)s')
    handler.setFormatter(formatter)
    logger.setLevel(getattr(logging, LOG_LEVEL))
    logger.addHandler(handler)
    return logger

def resp_beacon_gif(resp):
    resp.append_header('Cache-Control',
                       'no-cache, no-store, must-revalidate')
    resp.append_header('expires', 'Mon, 01 Jan 1990 00:00:00 GMT')
    resp.append_header('pragma', 'no-cache')
    resp.append_header('Content-type', 'image/gif')
    resp.body = base64.b64decode('R0lGODlhAQABAID/AP///wAA'
                                 'ACwAAAAAAQABAAACAkQBADs=')
