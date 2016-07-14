import falcon
from swallow import SwallowResource
from pirate import PirateResource
from healthcheck import HelthCheckResource
from okeanides import StaticResource
from dump import DumpDataResource

app = falcon.API()
app.add_route('/swallow', SwallowResource())
app.add_route('/swallow/{site_name}', SwallowResource())
app.add_route('/pirate/{site_name}', PirateResource())
app.add_route('/lb', HelthCheckResource())
app.add_route('/static/{filetype}/{name}', StaticResource())
app.add_route('/dump', DumpDataResource())
