import json
from collections import defaultdict, OrderedDict
from itertools import chain
from datetime import timedelta, date

from django.apps import apps
from django.shortcuts import render, get_object_or_404
from django.http import Http404, JsonResponse, HttpResponse
from django.core.urlresolvers import reverse, reverse_lazy

from django.views.generic.edit import CreateView, ModelFormMixin
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView, DeleteView



from django.views.decorators.http import require_http_methods
from django.shortcuts import redirect

from django.db.models import Count

from themenu.models import Dish, Meal, Course, Tag, GroceryListItem
from themenu.forms import DishModelForm, MealModelForm, TagModelForm


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
    # Sort the (ingrdient, [grocery,..], purchased) tuples with
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
        weekplan = OrderedDict()
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
    context['today'] = date.today()

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


class DishUpdateView(UpdateView):
    model = Dish
    form_class = DishModelForm

    # This now happens in model "get_absolute_url"
    # def get_success_url(self):
    #     return reverse('dish-detail', kwargs={'pk': self.object.id})

    def get_context_data(self, **kwargs):
        context = super(DishUpdateView, self).get_context_data(**kwargs)
        # If we need to add extra items to what passes to the template
        # context['now'] = timezone.now()
        return context


class DishCreateView(CreateView):
    model = Dish
    form_class = DishModelForm


class DishDeleteView(DeleteView):
    model = Dish
    success_url = reverse_lazy('calendar', args=(0,))


# Including this for when we want to only allow the owner to
# Delete the item
# class MyDeleteView(DeleteView):
#     def get_object(self, queryset=None):
#         """ Hook to ensure object is owned by request.user. """
#         obj = super(MyDeleteView, self).get_object()
#         if not obj.owner == self.request.user:
#             raise Http404
#         return obj

class MealDeleteView(DeleteView):
    model = Meal
    success_url = reverse_lazy('calendar', args=(0,))


class MealUpdateView(UpdateView):
    # model = Meal
    form_class = MealModelForm


class MealCreateView(CreateView):
    model = Meal
    form_class = MealModelForm

    def get_initial(self):
        """Get all the url params that are field names"""
        initial = {}
        for field in get_fields(Meal):
            initial[field] = self.request.GET.get(field)
        return initial

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()
        for dish in form.cleaned_data['dishes']:
            course = Course(meal=self.object, dish=dish)
            course.save()
        for tag in form.cleaned_data['tags']:
            self.object.tags.add(tag)
        return super(ModelFormMixin, self).form_valid(form)


class MealDetailView(DetailView):
    model = Meal


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


class TagUpdateView(UpdateView):
    model = Tag
    form_class = TagModelForm

    def get_context_data(self, **kwargs):
        context = super(TagUpdateView, self).get_context_data(**kwargs)
        # If we need to add extra items to what passes to the template
        # context['now'] = timezone.now()
        return context


class TagCreateView(CreateView):
    model = Tag
    form_class = TagModelForm


class TagDeleteView(DeleteView):
    model = Tag
    success_url = reverse_lazy('calendar', args=(0,))


# From https://docs.djangoproject.com/en/1.9/ref/models/meta/#migrating-from-the-old-api
# MyModel._meta.get_fields_with_model() becomes:


def get_fields(model):
    return list(set(chain.from_iterable(
        (field.name, field.attname) if hasattr(field, 'attname') else (field.name,)
        for field in model._meta.get_fields()
        # For complete backwards compatibility, you may want to exclude
        # GenericForeignKey from the results.
        if not field.is_relation
            or field.one_to_one
            or (field.many_to_one and field.related_model)
        # if not (field.many_to_one and field.related_model is None)
    )))

# In [93]: Meal._meta.get_fields()
# Out[93]:
# (<ManyToOneRel: themenu.course>,
#  <django.db.models.fields.AutoField: id>,
#  <django.db.models.fields.CharField: meal_type>,
#  <django.db.models.fields.DateField: date>,
#  <django.db.models.fields.related.ManyToManyField: dishes>,
#  <django.db.models.fields.related.ManyToManyField: tags>)

# In [94]: Tag._meta.get_fields()
# Out[94]:
# (<ManyToManyRel: themenu.ingredient>,
#  <ManyToManyRel: themenu.dish>,
#  <ManyToManyRel: themenu.meal>,
#  <django.db.models.fields.AutoField: id>,
#  <django.db.models.fields.TextField: name>,
#  <django.db.models.fields.TextField: color>)


def model_json_view(request, model_name):
    model = apps.get_model('themenu', model_name.title())
    order_by = request.GET.get('order_by')

    # model_fields = list(model._meta.get_fields())
    model_fields = get_fields(model)
    base_query_set = model.objects.values(*[str(f) for f in model_fields])

    if order_by:
        base_query_set = base_query_set.order_by(order_by)

    tag_query_set = list(base_query_set)
    return JsonResponse(tag_query_set, safe=False)
