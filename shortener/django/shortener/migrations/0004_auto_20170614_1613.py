# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-06-14 07:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shortener', '0003_auto_20170509_1024'),
    ]

    operations = [
        migrations.AlterField(
            model_name='url',
            name='short_id',
            field=models.SlugField(max_length=8, primary_key=True, serialize=False),
        ),
    ]