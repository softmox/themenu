from django import forms
from django.utils.datastructures import MultiValueDict

from django_select2.forms import (
    ModelSelect2MultipleWidget,
    ModelSelect2Widget,
)

from .models import Dish, Meal, Tag, Ingredient


class NameSearchFieldMixin(object):
    search_fields = [
        'name__icontains',
        'pk__startswith'
    ]


class NameSelect2MultipleWidget(NameSearchFieldMixin, ModelSelect2MultipleWidget):
    """This just combines the library's Select2 multiple widget
    with the ability to search by name or pk"""
    pass


class NameSelect2Widget(NameSearchFieldMixin, ModelSelect2Widget):
    pass


class IngredientSelect2Widget(NameSelect2Widget):
    def get_queryset(self):
        return Ingredient.objects.all()

    def value_from_datadict(self, data, files, name):
        if isinstance(data, MultiValueDict):
            return [d for d in data.getlist(name) if d]
        return data.get(name)


class IngredientSearchForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = ['name']
        widgets = {
            'name': IngredientSelect2Widget,
        }


class IngredientField(forms.ModelMultipleChoiceField):
    def to_python(self, value):
        if not value:
            return []
        else:
            return [item for item in value if item]


class DishForm(forms.ModelForm):
    class Meta:
        model = Dish
        fields = ['name', 'notes', 'source', 'recipe', 'tags']

        widgets = {
            'tags': NameSelect2MultipleWidget,
        }

    ingredient = IngredientField(required=False,
                                 widget=IngredientSelect2Widget,
                                 queryset=Ingredient.objects.all())
    amount = forms.CharField(max_length=100, required=False)


class MealModelForm(forms.ModelForm):
    """Like a normal ModelForm, but the Many-to-Many fields
    use the prettier select2 multiple fields"""
    class Meta:
        model = Meal
        fields = ['meal_type', 'date', 'dishes', 'tags', 'meal_type', 'meal_prep']

        widgets = {
            'dishes': NameSelect2MultipleWidget,
            'tags': NameSelect2MultipleWidget,
            'date': forms.DateInput(attrs={'type': 'date'})
        }


# TODO (Anne):  Do we want the colors to be choices? or is a textbox fine?
class TagModelForm(forms.ModelForm):

    class Meta:
        model = Tag
        fields = ['name']


class IngredientModelForm(forms.ModelForm):
    """Like a normal ModelForm, but the Many-to-Many fields
    use the prettier select2 multiple fields"""
    class Meta:
        model = Ingredient
        fields = ['name', 'tags']

        widgets = {
            'name': forms.TextInput(attrs={'size': 40}),
            'tags': NameSelect2MultipleWidget,

        }
