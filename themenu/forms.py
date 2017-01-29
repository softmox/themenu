from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model

from django_select2.forms import (
    ModelSelect2MultipleWidget,
    ModelSelect2Widget,
)

from registration.forms import RegistrationForm

from .models import Dish, Meal, Tag, Ingredient, MyUser


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


class NameSelect2Widget(NameSearchFieldMixin, ModelSelect2Widget):
    pass


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


class IngredientSelect2Widget(NameSelect2Widget):
    def get_queryset(self):
        return Ingredient.objects.all()

class IngredientSearchForm(forms.ModelForm):
    # name = forms.CharField(label='Ingredient Name', max_length=100)

    class Meta:
        model = Ingredient
        fields = ['name']
        widgets = {
            'name': IngredientSelect2Widget,
        }

# User = get_user_model()

# class TeamRegistrationForm(RegistrationForm):
#     class Meta(RegistrationForm.Meta):
#         model = MyUser
#         fields = [
#             User.USERNAME_FIELD,
#             'email',
#             'password1',
#             'password2',
#             'team'
#         ]
#         required_css_class = 'required'
#         widgets = {
#             'team': NameSelect2MultipleWidget,

#         }
