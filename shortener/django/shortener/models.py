# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin


class Beacon(models.Model):
    label = models.CharField(max_length=256)
    endpoint = models.URLField(max_length=256,
                               help_text="ex. https://oceanus.bizocean.co.jp/swallow/bizocean")

    def __str__(self):
        return self.label


class Url(models.Model):
    short_id = models.SlugField(max_length=16, primary_key=True)
    url = models.URLField(max_length=512)
    create_date = models.DateTimeField(auto_now=True)
    beacon = models.ForeignKey(Beacon)
    beacon_parameters = models.CharField(max_length=512,
                                         blank=True,
                                         help_text="ex. tit=mail_magazine_title&oid=2")
    author = models.ForeignKey(User)

    def omit_url(self):
        max_length = 50
        if len(self.url) < max_length:
            return self.url
        else:
            half_num = max_length // 2 - 2
            return "{} ... {}".format(self.url[:half_num], self.url[-half_num:])

    def __str__(self):
        return self.short_id


class UrlAdmin(admin.ModelAdmin):
    list_display = ("create_date", "short_id", "omit_url",
                    "beacon_parameters", "beacon")
    search_fields = ['url', 'beacon_parameters', 'short_id']
    ordering = ["-create_date"]
