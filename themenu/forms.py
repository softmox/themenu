from django import forms

from django_select2.forms import ModelSelect2MultipleWidget

from .models import Dish


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
