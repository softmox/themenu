from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView
from django.views.decorators.http import require_http_methods
from django.shortcuts import redirect
from datetime import timedelta, date

from collections import Counter
from itertools import cycle
import random

from .models import Tag, Ingredient, Dish, Menu, Meal
from django.contrib.auth.models import User


def index(request):
    return redirect('calendar', offset=0)

def calendar(request, offset):
    def weekdays(offset):
        today = date.today()
        weekdays = [today + timedelta(days=7*offset + i) for i in range(0 - today.weekday(), 7 - today.weekday())]
        return weekdays

    def get_meals_by_type(mealtype, offset):
        meals = Meal.objects.filter(date__range=(weekdays(offset)[0], weekdays(offset)[-1]), meal_type=mealtype)
        return meals

    def weekplan(offset):
        weekplan = {}
        for t in Meal.MEAL_TYPE_CHOICES:
            weekplan[t] = get_meals_by_type(t, offset)
        return weekplan

    context = {}
    offset = int(offset)
    context['weekplan'] = weekplan(offset)
    context['lastoffset'] = offset - 1
    context['nextoffset'] = offset + 1

    return render(request, 'themenu/calendar.html', context)
