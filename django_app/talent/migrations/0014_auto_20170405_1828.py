# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-05 09:28
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('talent', '0013_auto_20170405_1827'),
    ]

    operations = [
        migrations.RenameField(
            model_name='talent',
            old_name='class_title',
            new_name='title',
        ),
    ]
