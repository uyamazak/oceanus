from os import environ
from urllib.parse import urlencode, quote
from urllib.request import Request, urlopen
from task.celery_app import app, logger
import json

MARKEMEDIA_SEND_URL = environ['MARKEMEDIA_SEND_URL']
MARKEMEDIA_AUTH_CODE = environ['MARKEMEDIA_AUTH_CODE']


@app.task(bind=True)
def send2markemedia(self, form_data):
    logger.info("form_data:{}".format(form_data))
    logger.info("url:{}".format(MARKEMEDIA_SEND_URL))
    logger.info("code:{}".format(MARKEMEDIA_AUTH_CODE))
    try:
        form_data = json.dumps(form_data, separators=(',', ':'))
        post_fields = {"auth_cd": MARKEMEDIA_AUTH_CODE, "form_data": form_data}
        encoded_post_fields = urlencode(post_fields, quote_via=quote).encode()
    except Exception as e:
        logger.error("Markemedia encode error:{} form_data:{}".format(e, form_data))
        return

    try:
        response = ""
        request = Request(MARKEMEDIA_SEND_URL, encoded_post_fields)
        response = urlopen(request).read().decode('utf8')
        logger.error("Send post to Markemedia. response: {} "
                     "post_fields: {} "
                     "encoded_post_fields: {} ".format(response,
                                                       post_fields,
                                                       encoded_post_fields,
                                                       form_data))

    except Exception as e:
        logger.error("Markemedia request error:{} response:{} post_fields:{}".format(e, response, post_fields))
