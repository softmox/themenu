# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-10 19:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('themenu', '0002_auto_20161210_1916'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dayplan',
            name='date',
            field=models.DateField(verbose_name=b'plan date'),
        ),
    ]