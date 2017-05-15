# coding:utf-8
import random
import string
import json
import logging
import re
from urllib2 import urlopen
from urllib import urlencode
from urlparse import parse_qs
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_protect
from shortener.models import Url, Beacon
logger = logging.getLogger(__name__)


@login_required
@csrf_protect
def make(request):
    beacons = Beacon.objects.order_by("-pk")
    c = {"beacons": beacons}
    c.update(request)
    return render(request, 'shortener/make.html', c)


@login_required
@csrf_protect
def make_article(request):
    beacons = Beacon.objects.order_by("-pk")
    if request.method == 'POST':
        article = request.POST.get("article", '')
        beacon_id = int(request.POST.get('beacon', ''))
        beacon_parameters_org = request.POST.get('parameters', '').strip()
        beacon_parameters = beacon_parameters_org
        beacon = get_object_or_404(Beacon, pk=beacon_id)
        beacon_parameters_dict = parse_qs(beacon_parameters.encode('utf-8'))
        logger.info(beacon_parameters_dict)
        pat = re.compile(r"https?://[\w/:%#\$&\?\(\)~\.=\+\-]+")
        matchs = re.findall(pat, article)
        article = request.POST.get("article", '')
        converted_article = article
        if matchs:
            tit = beacon_parameters_dict.get('tit')
            if tit:
                tit = tit[0]
            for index, org_url in enumerate(matchs):
                logger.info(org_url)
                logger.info(tit)
                if tit:
                    beacon_parameters_dict['tit'] = tit + '_' + str(index)
                    beacon_parameters = urlencode(beacon_parameters_dict, doseq=True)
                short_id = _get_short_code(org_url,
                                           beacon,
                                           beacon_parameters,
                                           request.user)
                url_obj = Url(url=org_url,
                              short_id=short_id,
                              beacon=beacon,
                              beacon_parameters=beacon_parameters,
                              author=request.user)
                url_obj.save()
                converted_article = converted_article.replace(org_url, settings.SITE_URL + "/" + short_id)

        c = {"beacon": beacon,
             "beacons": beacons,
             "article": article,
             "converted_article": converted_article,
             "parameters": beacon_parameters_org
             }
    else:
        c = {"beacons": beacons}

    return render(request, 'shortener/make_article.html', c)

def index(request):
    """dummy page"""
    return render(request, 'shortener/index.html')


def _send_beacon(beacon_url):
    try:
        r = urlopen(beacon_url)
    except Exception as e:
        logging.info("urlopen error: ".format(e))
    else:
        logging.info(r.read())


def _create_beacon_url(url_obj, request):
    endpoint = url_obj.beacon.endpoint
    parameters = {
        "url": url_obj.url,
        "sid": request.COOKIES.get("oceanus_sid", ""),
        "oid": "2",
        "tit": "",
        "evt": "redirect",
        "rad": request.META.get("REMOTE_ADDR", ""),
        "ua":  request.META.get("HTTP_USER_AGENT", ""),
        "ref": request.META.get("HTTP_REFERER", settings.SITE_URL + "/" + url_obj.short_id),
    }
    if url_obj.beacon_parameters:
        encoded_beacon_parameters = parse_qs(url_obj.beacon_parameters.encode('utf-8'))
        parameters.update(encoded_beacon_parameters)
    parameters.update(request.GET)
    query_string = urlencode(parameters, doseq=True)
    logging.info(endpoint + "?" + query_string)
    return endpoint + "?" + query_string


def redirect_original(request, short_id):
    logger.info(request.META)
    url_obj = get_object_or_404(Url, pk=short_id)
    beacon_url = _create_beacon_url(url_obj, request)
    _send_beacon(beacon_url)
    return HttpResponseRedirect(url_obj.url)


@login_required
def shorten_url(request):
    url = request.POST.get("url", '')
    beacon_id = int(request.POST.get('beacon', ''))
    beacon_parameters = request.POST.get('parameters', '')
    beacon = get_object_or_404(Beacon, pk=beacon_id)
    if not (url == ''):
        short_id = _get_short_code(url,
                                   beacon,
                                   beacon_parameters,
                                   request.user)
        url_obj = Url(url=url,
                      short_id=short_id,
                      beacon=beacon,
                      beacon_parameters=beacon_parameters,
                      author=request.user)
        url_obj.save()

        response_data = {}
        response_data['url'] = settings.SITE_URL + "/" + short_id
        beacon_url = _create_beacon_url(url_obj, request)
        response_data['beacon_url'] = beacon_url
        return HttpResponse(json.dumps(response_data),
                            content_type="application/json")

    return HttpResponse(json.dumps({"error": "error occurs"}),
                        content_type="application/json")


def _get_short_code(url, beacon, beacon_parameters, author):
    length = 6
    logging.info("_get_short_code")
    logging.info(beacon_parameters)
    exists = Url.objects.filter(url=url,
                                beacon=beacon,
                                beacon_parameters=beacon_parameters,
                                author=author).order_by("-pk")
    if exists:
        return exists[0].short_id

    char = string.ascii_uppercase + string.digits + string.ascii_lowercase
    # if the randomly generated short_id is used then generate next
    while True:
        short_id = ''.join(random.choice(char) for x in range(length))
        try:
            Url.objects.get(pk=short_id)
        except Exception:
            return short_id
