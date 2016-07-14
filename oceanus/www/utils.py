import logging
import os
import base64

def oceanus_logging():
    LOG_LEVEL = os.environ['LOG_LEVEL']
    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler()
    logger.setLevel(getattr(logging, LOG_LEVEL))
    logger.addHandler(handler)
    return logger

def beacon_gif():
    return base64.b64decode('R0lGODlhAQABAID/AP///wAA'
                            'ACwAAAAAAQABAAACAkQBADs=')
