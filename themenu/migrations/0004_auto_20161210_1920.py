# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-10 19:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('themenu', '0003_auto_20161210_1918'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menu',
            name='dishes',
            field=models.ManyToManyField(blank=True, to='themenu.Dish'),
        ),
    ]