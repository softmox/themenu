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
        print("my value from data dict")
        if isinstance(data, MultiValueDict):
            return data.getlist(name)
        return data.get(name)


class IngredientSearchForm(forms.ModelForm):
    # name = forms.CharField(label='Ingredient Name', max_length=100)

    class Meta:
        model = Ingredient
        fields = ['name']
        widgets = {
            'name': IngredientSelect2Widget,
        }

class DishModelForm(forms.ModelForm):
    """Like a normal ModelForm, but the Many-to-Many fields
    use the prettier select2 multiple fields"""
    class Meta:
        model = Dish
        fields = ['name', 'notes', 'source', 'recipe', 'ingredient_amounts', 'tags']

        widgets = {
            'ingredient_amounts': NameSelect2MultipleWidget,
            'tags': NameSelect2MultipleWidget,
        }


class IngredientField(forms.MultipleChoiceField):
    def to_python(self, value):
        """Normalize data to a list of strings."""
        # Return an empty list if no input was given.
        print('TO PYTHON')
        print(value)
        print(type(value))
        if not value:
            return []
        # return value.split(',')
        return value

    def validate(self, value):
        print('VALIDATE')
        print(value)
        return True

# class DishForm(forms.Form):
class DishForm(forms.ModelForm):
    class Meta:
        model = Dish
        fields = ['name', 'notes', 'source', 'recipe', 'tags']

        widgets = {
            'tags': NameSelect2MultipleWidget,
        }

    # name = forms.CharField(max_length=500, widget=forms.TextInput(attrs={'size': 50}))
    # notes = forms.CharField(widget=forms.Textarea)
    # source = forms.CharField(max_length=500, widget=forms.TextInput(attrs={'size': 50}))
    # recipe = forms.CharField(widget=forms.Textarea)
    # ingredient = IngredientField(required=False, widget=IngredientSelect2Widget)
    ingredient = forms.ModelMultipleChoiceField(required=False,
                                           widget=IngredientSelect2Widget,
                                           queryset=Ingredient.objects.all())
    amount = forms.CharField(max_length=100, required=False)
    # tags = forms.MultipleChoiceField(widget=NameSelect2MultipleWidget(queryset=Tag.objects.all()), required=False)

    # Example (originally had "title" as a field'
    # def clean_title(self):
    #     if len(self.cleaned_data['title']) < 3:
    #         raise forms.ValidationError("Title must have more than 3 characters.")
    #     return self.cleaned_data["title"]


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

