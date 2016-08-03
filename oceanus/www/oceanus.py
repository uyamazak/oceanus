import falcon
from swallow import SwallowResource
from pirate import PirateResource
from healthcheck import HealthCheckResource, RedisStatusResource
from okeanides import StaticResource, RobotsTxtResource, FaviconIcoResource
from dump import DumpDataResource

app = falcon.API()
app.add_route('/swallow', SwallowResource())
app.add_route('/swallow/{site_name}', SwallowResource())
app.add_route('/pirate/{site_name}', PirateResource())
app.add_route('/lb', HealthCheckResource())
app.add_route('/rstatus', RedisStatusResource())

app.add_route('/static/{filetype}/{name}', StaticResource())
app.add_route('/favicon.ico', FaviconIcoResource())
app.add_route('/robots.txt', RobotsTxtResource())

app.add_route('/dump', DumpDataResource())
