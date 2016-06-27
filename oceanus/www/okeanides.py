import os
import falcon
OCEANUS_SWALLOW_HOST = os.environ['OCEANUS_SWALLOW_HOST']


class JsResource(object):

    def on_get(self, req, resp, name):
        resp.status = falcon.HTTP_200
        resp.content_type = 'text/javascript'
        resp.set_header('Access-Control-Allow-Origin', '*')
        name = os.path.normpath(name)
        try:
            with open('okeanides/' + name, 'r') as f:
                raw_body = f.read()
        except Exception as e:
            resp.body = "{0} {1}".format(e, name)
            resp.status = falcon.HTTP_404
            return
        else:
            resp.body = raw_body.replace('{%oceanus_host%}',
                                         OCEANUS_SWALLOW_HOST)
