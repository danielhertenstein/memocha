# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-31 19:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recorder', '0002_video_approved'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='approved',
            field=models.NullBooleanField(),
        ),
    ]