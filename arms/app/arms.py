import falcon
from resources.swallow import SwallowResource
from resources.pirate import PirateResource
from resources.gaze import GazeResource
from resources.pierce import PierceResource
from resources.healthcheck import HealthCheckResource, RedisStatusResource
from resources.static import (StaticResource,
                              RobotsTxtResource,
                              FaviconIcoResource)

app = falcon.API()
app.req_options.auto_parse_form_urlencoded = True

app.add_route('/swallow', SwallowResource())
app.add_route('/swallow/{site_name}', SwallowResource())
app.add_route('/pirate/{site_name}', PirateResource())
app.add_route('/gaze/{site_name}', GazeResource())
app.add_route('/pierce/{site_name}', PierceResource())

app.add_route('/lb', HealthCheckResource())
app.add_route('/hc', HealthCheckResource())
app.add_route('/rstatus', RedisStatusResource())

app.add_route('/static/{filetype}/{name}', StaticResource())
app.add_route('/favicon.ico', FaviconIcoResource())
app.add_route('/robots.txt', RobotsTxtResource())
