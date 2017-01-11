from django import forms

from django_select2.forms import ModelSelect2MultipleWidget


from .models import Dish, Meal


class NameSearchFieldMixin(object):
    search_fields = [
        'name__icontains',
        'pk__startswith'
    ]


class NameModelSelect2MultipleWidget(NameSearchFieldMixin, ModelSelect2MultipleWidget):
    """This just combines the library's Select2 multiple widget
    with the ability to search by name or pk"""
    pass


class DishModelSelect2MultipleWidgetForm(forms.ModelForm):
    """Like a normal ModelForm, but the Many-to-Many fields
    use the prettier select2 multiple fields"""
    class Meta:
        model = Dish
        fields = ['name', 'notes', 'source', 'recipe', 'speed',
                  'ease', 'results', 'ingredients', 'tags']

        widgets = {
            'ingredients': NameModelSelect2MultipleWidget,
            'tags': NameModelSelect2MultipleWidget,
        }


class MealModelSelect2MultipleWidgetForm(forms.ModelForm):
    """Like a normal ModelForm, but the Many-to-Many fields
    use the prettier select2 multiple fields"""
    class Meta:
        model = Meal
        fields = ['meal_type', 'date', 'dishes', 'tags', 'meal_type']

        widgets = {
            'dishes': NameModelSelect2MultipleWidget,
            'tags': NameModelSelect2MultipleWidget,
            'date': forms.DateInput(attrs={'type': 'date'})
        }
