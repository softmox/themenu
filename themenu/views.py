import json
from collections import defaultdict
from datetime import timedelta, date

from django.shortcuts import render, get_object_or_404
from django.http import Http404, JsonResponse
from django.core.urlresolvers import reverse, reverse_lazy

from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView

from django.views.decorators.http import require_http_methods
from django.shortcuts import redirect

from django.db.models import Count

from .models import Dish, Meal, Course, Tag, GroceryListItem #  , Ingredient


def index(request):
    return redirect('calendar', offset=0)


def grocery_list(request):
    grocery_list = GroceryListItem.objects.filter(
                    course__meal__date__gte=date.today()).order_by(
                    'purchased', 'course__meal__date')
    ingredient_to_grocery_list = defaultdict(list)
    for grocery_item in grocery_list:
        ingredient_to_grocery_list[grocery_item.ingredient.name].append(grocery_item)
    # Add a third item to the tuples:
    # a bool if all groceries have been purchased
    mark_all_purchased = [
        (ing, g_list, all(g.purchased for g in g_list))
        for ing, g_list in ingredient_to_grocery_list.items()
    ]
    # Sort the (ingrdient, [grocery,..]) tuples with
    # ones where everything has been purchased last
    sorted_items = sorted(mark_all_purchased, key=lambda x: x[2])

    context = {
        'ingredient_to_grocery_list': sorted_items
    }
    return render(request, 'themenu/grocery_list.html', context)


def refdate(offset):
    today = date.today()
    ref_date = today + timedelta(days=7 * offset)
    return ref_date


def calendar(request, offset):
    offset = offset

    def weekdays():
        weekdays_list = [refdate(offset) + timedelta(days=i)
                         for i in range(0 - refdate(offset).weekday(), 7 - refdate(offset).weekday())]
        return weekdays_list

    def get_meal_by_type_and_date(mealtype, date):
        try:
            thismeal = Meal.objects.get(date=date, meal_type=mealtype)
            return thismeal
        except Meal.DoesNotExist:
            return None

    def weekplan(weekdays_list):
        weekplan = {}
        meal_types = [i[1] for i in Meal.MEAL_TYPE_CHOICES]
        for type_ in meal_types:
            days = []
            for day in weekdays_list:
                days.append({'date': day,
                             'daymeal': get_meal_by_type_and_date(type_, day)})
            weekplan[type_] = days
        return weekplan

    def monday(valence):
        monday = refdate(offset) + timedelta(days=(7 * valence - refdate(offset).weekday()))
        prettymonday = monday.strftime('%d %B, %Y')
        return prettymonday

    context = {}
    offset = int(offset)
    context['weekplan'] = weekplan(weekdays())
    context['lastoffset'] = offset - 1
    context['nextoffset'] = offset + 1
    context['meal_choices'] = Meal.MEAL_TYPE_CHOICES
    context['thisweekmonday'] = monday(0)
    context['lastweekmonday'] = monday(-1)
    context['nextweekmonday'] = monday(1)

    return render(request, 'themenu/calendar.html', context)


@require_http_methods(["POST"])
def course_update(request):
    posted_data = json.loads(request.body)
    meal = get_object_or_404(Meal, id=posted_data['mealId'])
    dish = get_object_or_404(Dish, id=posted_data['dishId'])
    course = Course.objects.get(meal=meal, dish=dish)
    attribute = posted_data['attribute']
    value = posted_data['checked']
    if attribute == 'eaten':
        course.eaten = value
        course.save(update_fields=['eaten'])
    elif attribute == 'prepared':
        course.prepared = value
        course.save(update_fields=['prepared'])

    return JsonResponse({"OK": True})


@require_http_methods(["POST"])
def grocery_update(request):
    posted_data = json.loads(request.body)
    grocery = get_object_or_404(GroceryListItem, id=posted_data['groceryId'])
    value = posted_data['checked']
    grocery.purchased = value
    grocery.save(update_fields=['purchased'])
    return JsonResponse({"OK": True})


class DishDetailView(DetailView):
    model = Dish

    def get_context_data(self, **kwargs):
        context = super(DishDetailView, self).get_context_data(**kwargs)
        # If we need to add extra items to what passes to the template
        # context['now'] = timezone.now()
        return context


class MealDetailView(DetailView):
    model = Meal

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except Http404:
            # TODO: What do we wanna show them for invalid Meal?
            return redirect('calendar', offset=0)

        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

class TagDetailView(DetailView):
    model = Tag

    def get_context_data(self, **kwargs):
        this_tag = self.object
        tag_dishes = this_tag.dish_set
        tag_ing = this_tag.ingredient_set
        tag_meals = this_tag.meal_set
        context = super(TagDetailView, self).get_context_data(**kwargs)
        context['dish_count'] = tag_dishes.count()
        context['dishes'] = tag_dishes.annotate(num_meals=Count('meal')).order_by('-num_meals')[:15]
        context['ingredient_count'] = tag_ing.count()
        context['ingredients'] = tag_ing.annotate(num_dishes=Count('dish')).order_by('-num_dishes')[:15]
        context['meal_count'] = tag_meals.count()
        context['meals'] = tag_meals.order_by('-date')[:15]
        # If we need to add extra items to what passes to the template
        # context['now'] = timezone.now()
        return context

class TagListView(ListView):
    model = Tag

    def get_context_data(self, **kwargs):
        context = super(TagListView, self).get_context_data(**kwargs)
        context['tags'] = Tag.objects.all().annotate(num_dishes=Count('dish', distinct=True),
                                             num_ingredients=Count('ingredient', distinct=True)
                                            ).order_by('-num_dishes')
        # If we need to add extra items to what passes to the template
        # context['now'] = timezone.now()
        return context

class DishUpdateView(UpdateView):
    model = Dish
    fields = ['name', 'notes', 'source', 'recipe', 'speed', 'ease', 'results', 'ingredients', 'tags']

    def get_success_url(self):
        return reverse('dish-detail', kwargs={'pk':self.object.id})

    def get_context_data(self, **kwargs):
        context = super(DishUpdateView, self).get_context_data(**kwargs)
        # If we need to add extra items to what passes to the template
        # context['now'] = timezone.now()
        return context

class DishCreateView(CreateView):
    model = Dish
    fields = ['name', 'notes', 'source', 'recipe', 'speed', 'ease', 'results', 'ingredients', 'tags']

    def get_success_url(self):
        return reverse('dish-detail', kwargs={'pk':self.object.id})
