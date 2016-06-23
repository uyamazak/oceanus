import os
import falcon
OCEANUS_SWALLOW_HOST = os.environ['OCEANUS_SWALLOW_HOST']


class JsResource(object):

    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.content_type = 'text/javascript'
        resp.set_header('Access-Control-Allow-Origin', '*')
        with open('okeanides.js', 'r') as f:
            raw_body = f.read()
        resp.body=raw_body.replace('{%oceanus_host%}', OCEANUS_SWALLOW_HOST)

