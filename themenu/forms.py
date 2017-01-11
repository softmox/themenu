from django.db import models
from django import forms

from django_select2.forms import (
    HeavySelect2MultipleWidget, HeavySelect2Widget, ModelSelect2MultipleWidget,
    ModelSelect2TagWidget, ModelSelect2Widget, Select2MultipleWidget,
    Select2Widget
)

from .models import Dish, Tag


class NameSearchFieldMixin(object):
    search_fields = [
        'name__icontains',
        'pk__startswith'
    ]


class NameModelSelect2MultipleWidget(NameSearchFieldMixin, ModelSelect2MultipleWidget):
    pass


class DishModelSelect2MultipleWidgetForm(forms.ModelForm):
    class Meta:
        model = Dish
        fields = ['name', 'notes', 'source', 'recipe', 'speed',
                  'ease', 'results', 'ingredients', 'tags']

        widgets = {
            'ingredients': NameModelSelect2MultipleWidget,
            'tags': NameModelSelect2MultipleWidget,
        }


# class DishModelSelect2MultipleWidgetForm(forms.Form):
#     name = forms.CharField(max_length=50)
#     tags = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
#         queryset=Tag.objects.all(),
#         search_fields=['name__icontains'],
#     ), queryset=Tag.objects.all(), required=False)
