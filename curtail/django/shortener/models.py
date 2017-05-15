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
    short_id = models.SlugField(max_length=6, primary_key=True)
    url = models.URLField(max_length=512)
    create_date = models.DateTimeField(auto_now=True)
    beacon = models.ForeignKey(Beacon)
    beacon_parameters = models.CharField(max_length=512,
                                         blank=True,
                                         help_text="ex. tit=mail_magazine_title&oid=2")
    author = models.ForeignKey(User)

    def __str__(self):
        return self.short_id


class UrlAdmin(admin.ModelAdmin):
    list_display = ("short_id", "url", "beacon",
                    "beacon_parameters", "create_date")
    search_fields = ['url', 'beacon_parameters', 'short_id']
