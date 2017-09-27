# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin


class Query(models.Model):
    title = models.CharField(max_length=256)
    description = models.TextField(blank=True)
    download_sql = models.TextField(help_text="適度にLIMIT 5000程度かけてください。"
                                              "{START_DATE} {END_DATE} がYYYY-MM-DD形式で置換されます")
    preview_sql = models.TextField(blank=True,
                                   help_text="LIMIT 100程度推奨かも。"
                                             "{START_DATE} {END_DATE} がYYYY-MM-DD形式で置換されます")

    use_legacy_sql = models.BooleanField(default=True, help_text="スタンダードSQLを使いたい場合はチェックを外してください。")
    use_custom_replacement = models.BooleanField(default=False, help_text="START_DATE, END_DATE以外の置換を使いたい場合はチェックしてください")
    users = models.ManyToManyField(User, help_text="表示とCSVダウンロードできるユーザーを指定してください")
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    def short_description(self):
        return self.description[:50]


class QueryAdmin(admin.ModelAdmin):
    ordering = ["-create_date"]
    filter_horizontal = ["users"]
    list_display = ("title",
                    "short_description",
                    "create_date",
                    "update_date",
                    "use_legacy_sql",
                    "use_custom_replacement")
    save_as = True
