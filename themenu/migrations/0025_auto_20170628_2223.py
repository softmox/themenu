# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-06-29 03:23
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('themenu', '0024_meal_meal_prep'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='meal',
            unique_together=set([('date', 'meal_type', 'team')]),
        ),
    ]
