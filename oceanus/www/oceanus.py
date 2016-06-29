import falcon
import swallow
import healthcheck
import okeanides

app = falcon.API()
app.add_route('/swallow', swallow.SwallowResource())
app.add_route('/swallow/{site_name}', swallow.SwallowResource())
app.add_route('/lb', healthcheck.HelthCheckResource())
app.add_route('/okeanides/{name}', okeanides.JsResource())
