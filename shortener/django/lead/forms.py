# -*- coding: utf-8 -*-
import datetime
from django import forms
DEFAULT_DAYS_BEFORE = 7


class DateRageForm(forms.Form):
    start_date = forms.DateField(initial=datetime.date.today() - datetime.timedelta(days=DEFAULT_DAYS_BEFORE),
                                 label="開始日")
    end_date = forms.DateField(initial=datetime.date.today(),
                               label="終了日")


def create_form_from_placements(placements, data={}):
    f = forms.Form()
    f.is_bound = True
    for p in placements:
        f.fields[p] = forms.CharField(label=p,
                                      required=False,
                                      initial="")
    if not data.get("START_DATE"):
        data["START_DATE"] = datetime.date.today() - datetime.timedelta(days=DEFAULT_DAYS_BEFORE)

    if not data.get("END_DATE"):
        data["END_DATE"] = datetime.date.today()

    f.data = data
    f.full_clean()
    return f
