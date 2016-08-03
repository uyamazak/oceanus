import os
import falcon
OCEANUS_SWALLOW_HOST = os.environ['OCEANUS_SWALLOW_HOST']


class StaticResource(object):

    def on_get(self, req, resp, filetype, name):
        resp.status = falcon.HTTP_200
        if filetype == 'js':
            resp.content_type = 'text/javascript'
        elif filetype == 'html':
            resp.content_type = 'text/html'
        elif filetype == 'css':
            resp.content_type = 'text/css'
        else:
            resp.content_type = 'text/plain'
        resp.set_header('Access-Control-Allow-Origin', '*')
        name = os.path.normpath(name)
        filetype = os.path.normpath(filetype)
        file_path = os.path.join('static', filetype, name)
        try:
            with open(file_path, 'r', encoding='utf8') as f:
                raw_body = f.read()
        except Exception as e:
            resp.body = "{0} {1}".format(e, name)
            resp.status = falcon.HTTP_404
            return
        else:
            resp.body = raw_body.replace('{%oceanus_host%}',
                                         OCEANUS_SWALLOW_HOST)


class RobotsTxtResource(object):

    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.content_type = 'text/plain'
        with open('static/robots.txt', 'r') as f:
            raw_body = f.read()
        resp.body = raw_body


class FaviconIcoResource(object):

    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.content_type = "image/x-icon"
        with open('static/favicon.ico', 'rb') as f:
            raw_body = f.read()
        resp.body = raw_body
