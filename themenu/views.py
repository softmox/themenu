from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView

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
    offset = offset
    def refdate():
        today = date.today()
        refdate = today + timedelta(days=7*offset)
        return refdate

    def weekdays():
        weekdays = [refdate() + timedelta(days=i) for i in range(0 - refdate().weekday(), 7 - refdate().weekday())]
        return weekdays

    def get_meals_by_type(mealtype):
        meals = Meal.objects.filter(date__range=(weekdays()[0], weekdays()[-1]), meal_type=mealtype)
        return meals

    def weekplan():
        weekplan = {}
        mt = [i[1] for i in Meal.MEAL_TYPE_CHOICES]
        for t in mt:
            weekplan[t] = get_meals_by_type(t)
        return weekplan

    def monday(valence):
        monday = refdate() + timedelta(days=(7 * valence - refdate().weekday()))
        prettymonday = monday.strftime('%d %B, %Y')
        return prettymonday

    context = {}
    offset = int(offset)
    context['weekplan'] = weekplan()
    context['lastoffset'] = offset - 1
    context['nextoffset'] = offset + 1
    context['thisweekmonday'] = monday(0)
    context['lastweekmonday'] = monday(-1)
    context['nextweekmonday'] = monday(1)

    return render(request, 'themenu/calendar.html', context)


class DishDetailView(DetailView):
    model = Dish

    def get_context_data(self, **kwargs):
        context = super(DishDetailView, self).get_context_data(**kwargs)
        # context['now'] = timezone.now()
        return context
