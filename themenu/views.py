import json
from django.shortcuts import render, get_object_or_404
from django.http import Http404, JsonResponse
from django.core.urlresolvers import reverse

from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView

from django.views.decorators.http import require_http_methods
from django.shortcuts import redirect
from datetime import timedelta, date

from .models import Tag, Ingredient, Dish, Meal, Course


def index(request):
    return redirect('calendar', offset=0)


def calendar(request, offset):
    offset = offset

    def refdate():
        today = date.today()
        refdate = today + timedelta(days=7 * offset)
        return refdate

    def weekdays():
        weekdays = [refdate() + timedelta(days=i) for i in range(0 - refdate().weekday(), 7 - refdate().weekday())]
        return weekdays

    def get_meal_by_type_and_date(mealtype,date):
        try:
            thismeal = Meal.objects.get(date=date, meal_type=mealtype)
            return thismeal
        except Meal.DoesNotExist:
            return None

    def weekplan(weekdays):
        weekplan = {}
        mt = [i[1] for i in Meal.MEAL_TYPE_CHOICES]
        for t in mt:
            days = []
            for d in weekdays:
                days.append({'date': d,
                             'daymeal': get_meal_by_type_and_date(t,d)})
            weekplan[t] = days
        return weekplan

    def monday(valence):
        monday = refdate() + timedelta(days=(7 * valence - refdate().weekday()))
        prettymonday = monday.strftime('%d %B, %Y')
        return prettymonday

    context = {}
    offset = int(offset)
    context['weekplan'] = weekplan(weekdays())
    context['lastoffset'] = offset - 1
    context['nextoffset'] = offset + 1
    context['weekdays'] = weekdays()
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
    elif attribute == 'prepared':
        course.prepared = value
    course.save()

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
