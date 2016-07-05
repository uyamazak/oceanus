import falcon
import base64
import os
import logging
import json

LOG_LEVEL = os.environ['LOG_LEVEL']
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
logger.setLevel(getattr(logging, LOG_LEVEL))
logger.addHandler(handler)


class DumpDataResource(object):

    def on_get(self, req, resp):
        message = {"access_route": req.access_route}
        message.update(req.params)
        message.update(req.headers)
        message = json.dumps(message, sort_keys=True)
        logger.info("[dump]:{}".format(message))
        resp.status = falcon.HTTP_200

        if req.get_param('debug', required=False):
            resp.body = message
            return

        resp.append_header('Cache-Control', 'no-cache')
        resp.append_header('Content-type', 'image/gif')
        resp.body = base64.b64decode('R0lGODlhAQABAGAAACH5BAEKAP'
                                     '8ALAAAAAABAAEAAAgEAP8FBAA7')