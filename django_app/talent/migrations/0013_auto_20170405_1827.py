# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-05 09:27
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('talent', '0012_review_comment'),
    ]

    operations = [
        migrations.RenameField(
            model_name='talent',
            old_name='title',
            new_name='class_title',
        ),
    ]
