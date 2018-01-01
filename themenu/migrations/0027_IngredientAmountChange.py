# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2018-01-01 03:38
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


def create_dummy_ingredient_amounts(apps, schema_editor):
    """Make IngredientAmount instances with empty Amounts to fill"""
    Ingredient = apps.get_model('themenu', 'Ingredient')
    IngredientAmount = apps.get_model('themenu', 'IngredientAmount')
    for ingredient in Ingredient.objects.all():
        IngredientAmount(ingredient=ingredient).save()


class Migration(migrations.Migration):

    dependencies = [
        ('themenu', '0026_IngredientAmountAdd'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredientamount',
            name='amount',
            field=models.ForeignKey(null=True,
                                    on_delete=django.db.models.deletion.CASCADE,
                                    to='themenu.Amount'),
        ),
        migrations.RunPython(create_dummy_ingredient_amounts, reverse_code=migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='dish',
            name='ingredients',
        ),
        migrations.RemoveField(
            model_name='grocerylistitem',
            name='ingredient',
        ),
    ]
