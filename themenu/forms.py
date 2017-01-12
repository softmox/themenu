from django import forms

from django_select2.forms import ModelSelect2MultipleWidget


from .models import Dish, Meal


class NameSearchFieldMixin(object):
    search_fields = [
        'name__icontains',
        'pk__startswith'
    ]


class NameSelect2MultipleWidget(NameSearchFieldMixin, ModelSelect2MultipleWidget):
    """This just combines the library's Select2 multiple widget
    with the ability to search by name or pk"""
    pass


class DishModelForm(forms.ModelForm):
    """Like a normal ModelForm, but the Many-to-Many fields
    use the prettier select2 multiple fields"""
    class Meta:
        model = Dish
        fields = ['name', 'notes', 'source', 'recipe', 'speed',
                  'ease', 'results', 'ingredients', 'tags']

        widgets = {
            'ingredients': NameSelect2MultipleWidget,
            'tags': NameSelect2MultipleWidget,
        }


class MealModelForm(forms.ModelForm):
    """Like a normal ModelForm, but the Many-to-Many fields
    use the prettier select2 multiple fields"""
    class Meta:
        model = Meal
        fields = ['meal_type', 'date', 'dishes', 'tags', 'meal_type']

        widgets = {
            'dishes': NameSelect2MultipleWidget,
            'tags': NameSelect2MultipleWidget,
            'date': forms.DateInput(attrs={'type': 'date'})
        }
