# coding:utf-8
import logging
import unicodecsv as csv
import datetime
import re
from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.contrib.admin.views.decorators import staff_member_required
from google.cloud import bigquery
from lead.models import Query
from lead.forms import DateRageForm, create_form_from_placements

logging.basicConfig(format='%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

MAX_RESULTS = 5000


@csrf_protect
@login_required
def list_queries(request):
    queries = get_list_or_404(Query,
                              users__id=request.user.pk,
                              use_custom_replacement=False)
    context = {"queries": queries}
    return render(request, 'lead/list.html', context)


@csrf_protect
@staff_member_required
@login_required
def list_custom_queries(request):
    queries = get_list_or_404(Query,
                              users__id=request.user.pk,
                              use_custom_replacement=True)
    context = {"queries": queries}
    return render(request, 'lead/list_custom.html', context)


def _get_form_values(form):
    if form.is_valid():
        return form.cleaned_data
    else:
        logger.debug(form.fields)
        return {k: v.initial for k, v in form.fields.items()}


def _get_date_values(form):
    if form.is_valid():
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']
    else:
        start_date = form.fields.get("start_date").initial
        end_date = form.fields.get("end_date").initial
    logger.debug("(start_date, end_date):{}, {}".format(start_date, end_date))
    return (start_date, end_date)


def _get_placements(sql):
    pat = re.compile("\{([A-Z_]+)\}")
    matchs = pat.findall(sql)
    if matchs:
        return [r for r in matchs]

    return None


@csrf_protect
@login_required
def detail_query(request, query_id):
    query_obj = get_object_or_404(Query,
                                  pk=query_id,
                                  users__id=request.user.pk,
                                  use_custom_replacement=False)

    if request.method == "POST":
        form = DateRageForm(request.POST)
    else:
        form = DateRageForm()

    bq = None
    query_sql = None
    start_date, end_date = _get_date_values(form)
    if query_obj.preview_sql:
        query_sql = query_obj.preview_sql.format(START_DATE=start_date,
                                                 END_DATE=end_date)
        client = bigquery.Client()
        bq = client.run_sync_query(query_sql)
        bq.use_legacy_sql = query_obj.use_legacy_sql
        bq.max_results = MAX_RESULTS
        bq.run()

    context = {"query_obj": query_obj,
               "query_sql": query_sql,
               "results": bq,
               "form": form,
               "start_date": start_date.strftime("%Y-%m-%d"),
               "end_date": end_date.strftime("%Y-%m-%d"),
               }
    return render(request, 'lead/detail.html', context)


@csrf_protect
@login_required
@staff_member_required
def detail_custom_query(request, query_id):
    query_obj = get_object_or_404(Query,
                                  pk=query_id,
                                  users__id=request.user.pk,
                                  use_custom_replacement=True)

    placements = _get_placements(query_obj.preview_sql)
    if request.method == "POST":
        form = create_form_from_placements(placements, {k: v for k, v in request.POST.items()})
        replacements = _get_form_values(form)
        if query_obj.preview_sql:
            query_sql = query_obj.preview_sql.format(**replacements)
            client = bigquery.Client()
            bq = client.run_sync_query(query_sql)
            bq.use_legacy_sql = query_obj.use_legacy_sql
            bq.max_results = MAX_RESULTS
            bq.run()
            context = {"query_obj": query_obj,
                       "query_sql": query_sql,
                       "results": bq,
                       "form": form}
    else:
        form = create_form_from_placements(placements)
        context = {"query_obj": query_obj,
                   "form": form}
    logger.debug("placements: {}".format(placements))

    return render(request, 'lead/detail_custom.html', context)


def _convert_item(item, charset="cp932"):
    if item is None:
        return ""

    if isinstance(item, datetime.datetime):
        return item.strftime("%Y/%m/%d %H:%M:%S")

    if isinstance(item, int):
        item = "{}".format(item)

    return item.encode(charset, "replace")


@csrf_protect
@login_required
def download_query(request, query_id):
    query_obj = get_object_or_404(Query,
                                  pk=query_id,
                                  users__id=request.user.pk,
                                  use_custom_replacement=False)

    form = DateRageForm(request.GET)
    start_date, end_date = _get_date_values(form)
    query_sql = query_obj.download_sql.format(START_DATE=start_date,
                                              END_DATE=end_date)
    logger.debug("query_sql:{}".format(query_sql))
    client = bigquery.Client()
    bq = client.run_sync_query(query_sql)
    bq.use_legacy_sql = query_obj.use_legacy_sql
    bq.max_results = MAX_RESULTS
    bq.run()

    filename = "{}_{}_{}.csv".format(query_obj.pk,
                                     start_date,
                                     end_date)

    logger.info("download_query user:{} "
                "filename:{}".format(query_obj.pk,
                                     filename))

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename={}'.format(filename)

    writer = csv.writer(response)
    # header
    writer.writerow([s.name for s in bq.schema])
    # content
    for row in bq.rows:
        writer.writerow([_convert_item(r) for r in row])

    return response
