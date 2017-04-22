import json
from collections import defaultdict, OrderedDict
from itertools import chain
from datetime import timedelta, date, datetime

from django.apps import apps
from django.shortcuts import render, get_object_or_404
from django.http import Http404, JsonResponse, HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse, reverse_lazy

from django.views.generic.edit import CreateView, ModelFormMixin
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView, DeleteView


from django.views.decorators.http import require_http_methods
from django.shortcuts import redirect

from django.db.models import Count

from registration.views import RegistrationView

from themenu.models import (
    Dish,
    Meal,
    Course,
    Tag,
    Ingredient,
    GroceryListItem,
    RandomGroceryItem,
    MyUser,
    Team
)

from themenu.forms import (
    DishModelForm,
    MealModelForm,
    TagModelForm,
    IngredientModelForm,
)


def index(request):
    return redirect('calendar', view_date=datetime.strftime(date.today(), '%Y%m%d'))


def scores(request):
    context = {
    }
    return render(request, 'themenu/scores.html', context)


def grocery_list(request):
    def _get_meal_groceries(team):
        return GroceryListItem.objects.filter(course__meal__team=team)\
                                      .filter(course__meal__date__gte=date.today())\
                                      .order_by('purchased', 'course__meal__date')

    def _get_random_groceries(team):
        return RandomGroceryItem.objects.filter(team=team)\
                                        .filter(purchased=False)\
                                        .order_by('purchased')

    team = request.user.myuser.team
    if not team:
        # redirect to a team registration page
        # if you don't have a team, you can't plan meals
        # so why would you need a grocery list
        pass

    grocery_list = _get_meal_groceries(team)
    ingredient_to_grocery_list = defaultdict(list)
    for grocery_item in grocery_list:
        ingredient_to_grocery_list[grocery_item.ingredient.name].append(grocery_item)
    # Add a third item to the tuples:
    # a bool if all groceries have been purchased
    mark_all_purchased = [
        (ingredient, grocery_items, all(g.purchased for g in grocery_items))
        for ingredient, grocery_items in ingredient_to_grocery_list.items()
    ]
    # Sort the (ingrdient, [grocery,..], purchased) tuples with
    # ones where everything has been purchased last
    sorted_items = sorted(mark_all_purchased, key=lambda x: x[2])

    random_grocery_list = _get_random_groceries(team)
    context = {
        'ingredient_to_grocery_list': sorted_items,
        'random_grocery_list': random_grocery_list,
    }
    return render(request, 'themenu/grocery_list.html', context)


def calendar(request, view_date):
    parsed_date = datetime.strptime(str(view_date), '%Y%m%d')
    team = request.user.myuser.team

    def weekdays():
        weekdays_list = [parsed_date + timedelta(days=i)
                         for i in range(0 - parsed_date.weekday(), 7 - parsed_date.weekday())]
        return weekdays_list

    def get_meal_by_type_and_date(mealtype, date):
        try:
            thismeal = Meal.objects.get(date=date, meal_type=mealtype, team=team)
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
        monday = parsed_date + timedelta(days=(7 * valence - parsed_date.weekday()))
        prettymonday = monday.strftime('%d %B, %Y')
        return monday

    if not team:
        # redirect to a team register page
        # if you don't have a team, you can't plan meals
        pass

    context = {}
    context['weekplan'] = weekplan(weekdays())
    context['meal_choices'] = Meal.MEAL_TYPE_CHOICES
    context['thisweekmonday'] = monday(0).strftime('%d %B %Y')
    context['lastmondaydate'] = monday(-1).strftime('%Y%m%d')
    context['lastweekmonday'] = monday(-1).strftime('%d %B %Y')
    context['nextmondaydate'] = monday(1).strftime('%Y%m%d')
    context['nextweekmonday'] = monday(1).strftime('%d %B %Y')
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
    if posted_data['groceryType'] == 'meal':
        grocery = get_object_or_404(GroceryListItem, id=posted_data['groceryId'])
    elif posted_data['groceryType'] == 'random':
        grocery = get_object_or_404(RandomGroceryItem, id=posted_data['groceryId'])
    else:
        JsonResponse({"OK": False})

    value = posted_data['checked']
    grocery.purchased = value
    grocery.save(update_fields=['purchased'])
    return JsonResponse({"OK": True})


def dish_search(request):
    search_term = request.GET.get('text', '')
    matching_dishes = Dish.objects.filter(name__icontains=search_term)
    context = {
        'search_term': search_term,
        'matching_dishes': matching_dishes,
    }
    return render(request, 'themenu/dish_search.html', context)


class RandomGroceryItemCreate(CreateView):
    model = RandomGroceryItem
    fields = ['name']

    def get_initial(self):
        """Get all the url params that are field names"""
        team = get_object_or_404(Team, myuser=self.request.user.myuser)
        initial = {}
        initial['team_id'] = team.id
        return initial

    def form_valid(self, form):
        obj = form.save(commit=False)
        team = get_object_or_404(Team, myuser=self.request.user.myuser)
        obj.team = team
        obj.save()
        return super(RandomGroceryItemCreate, self).form_valid(form)


class DishDetail(DetailView):
    model = Dish

    def get_context_data(self, **kwargs):
        context = super(DishDetail, self).get_context_data(**kwargs)
        # If we need to add extra items to what passes to the template
        # context['now'] = timezone.now()
        return context


class DishUpdate(UpdateView):
    model = Dish
    form_class = DishModelForm

    # This now happens in model "get_absolute_url"
    # def get_success_url(self):
    #     return reverse('dish-detail', kwargs={'pk': self.object.id})

    def get_context_data(self, **kwargs):
        context = super(DishUpdate, self).get_context_data(**kwargs)
        # If we need to add extra items to what passes to the template
        # context['now'] = timezone.now()
        return context


class DishCreate(CreateView):
    model = Dish
    form_class = DishModelForm

    def form_valid(self, form):
        obj = form.save(commit=False)
        myuser = get_object_or_404(MyUser, user=self.request.user)
        obj.created_by = myuser
        obj.save()
        form.save_m2m()
        return HttpResponseRedirect(obj.get_absolute_url())


class DishDelete(DeleteView):
    model = Dish
    success_url = reverse_lazy('calendar', args=(0,))


class DishList(ListView):
    model = Dish

    def dishes_by_source(self):
        """Creates a dictionary mapping each source
        to a list of the dishes with that source"""
        by_source = defaultdict(list)
        all_dishes = Dish.objects.all()
        for dish in all_dishes:
            by_source[dish.source].append(dish)
        return by_source

    def get_context_data(self, **kwargs):
        context = super(DishList, self).get_context_data(**kwargs)
        context['dishes'] = self.dishes_by_source()
        return context

class MyUserDetail(DetailView):
    model = MyUser

class TeamCreate(CreateView):
    model = Team
    fields = ['name']

    def form_valid(self, form):
        obj = form.save(commit=True)
        myuser = get_object_or_404(MyUser, user=self.request.user)
        myuser.team = obj
        myuser.save()
        return HttpResponseRedirect(obj.get_absolute_url())

class TeamDetail(DetailView):
    model = Team

    def get_context_data(self, **kwargs):
        this_team = self.object
        context = super(TeamDetail, self).get_context_data(**kwargs)
        team_members = MyUser.objects.filter(team=this_team)
        context['member_count'] = team_members.count()
        context['team_members'] = team_members
        context['team'] = this_team
        return context

# Including this for when we want to only allow the owner to
# Delete the item
# class MyDelete(DeleteView):
#     def get_object(self, queryset=None):
#         """ Hook to ensure object is owned by request.user. """
#         obj = super(MyDeleteView, self).get_object()
#         if not obj.owner == self.request.user:
#             raise Http404
#         return obj

class MealDelete(DeleteView):
    model = Meal
    success_url = reverse_lazy('calendar', args=(0,))


class MealSaveMixin(ModelFormMixin):
    """Must do special work to add many-to-many models,
    especially with the intermediate model Course"""
    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()

        # Only remove tags and tags no longer specified by the form
        removed_tags = self.object.tags.exclude(id__in=form.cleaned_data['tags'])
        for t in removed_tags:
            self.object.tags.remove(t)

        # Intermediate model means you must clear all courses
        # https://docs.djangoproject.com/en/1.10/topics/db/models/#intermediary-manytomany
        self.object.dishes.clear()

        for dish in form.cleaned_data['dishes']:
            course = Course(meal=self.object, dish=dish)
            course.save()
        for tag in form.cleaned_data['tags'].exclude(id__in=self.object.tags.all()):
            self.object.tags.add(tag)
        return super(ModelFormMixin, self).form_valid(form)


class MealUpdate(MealSaveMixin, UpdateView):
    model = Meal
    form_class = MealModelForm

    def form_valid(self, form):
        return super(MealUpdate, self).form_valid(form)


class MealCreate(MealSaveMixin, CreateView):
    model = Meal
    form_class = MealModelForm

    def get_initial(self):
        """Get all the url params that are field names"""
        team = get_object_or_404(Team, myuser=self.request.user.myuser)
        initial = {}
        initial['team_id'] = team.id
        for field in get_fields(Meal):
            initial[field] = self.request.GET.get(field)
        return initial

    def form_valid(self, form):
        obj = form.save(commit=False)
        team = get_object_or_404(Team, myuser=self.request.user.myuser)
        obj.team = team
        obj.save()
        return super(MealCreate, self).form_valid(form)


class MealDetail(DetailView):
    model = Meal


class TagDetail(DetailView):
    model = Tag

    def get_context_data(self, **kwargs):
        this_tag = self.object
        tag_dishes = this_tag.dish_set
        tag_ing = this_tag.ingredient_set
        tag_meals = this_tag.meal_set
        context = super(TagDetail, self).get_context_data(**kwargs)
        context['dish_count'] = tag_dishes.count()
        context['dishes'] = tag_dishes.annotate(num_meals=Count('meal')).order_by('-num_meals')[:15]
        context['ingredient_count'] = tag_ing.count()
        context['ingredients'] = tag_ing.annotate(num_dishes=Count('dish')).order_by('-num_dishes')[:15]
        context['meal_count'] = tag_meals.count()
        context['meals'] = tag_meals.order_by('-date')[:15]
        # If we need to add extra items to what passes to the template
        # context['now'] = timezone.now()
        return context


class TagList(ListView):
    model = Tag

    def get_context_data(self, **kwargs):
        context = super(TagList, self).get_context_data(**kwargs)
        context['tags'] = Tag.objects.all().annotate(num_dishes=Count('dish', distinct=True),
                                             num_ingredients=Count('ingredient', distinct=True)
                                            ).order_by('-num_dishes')
        # If we need to add extra items to what passes to the template
        # context['now'] = timezone.now()
        return context


class TagUpdate(UpdateView):
    model = Tag
    form_class = TagModelForm

    def get_context_data(self, **kwargs):
        context = super(TagUpdate, self).get_context_data(**kwargs)
        # If we need to add extra items to what passes to the template
        # context['now'] = timezone.now()
        return context


class TagCreate(CreateView):
    model = Tag
    form_class = TagModelForm


class TagDelete(DeleteView):
    model = Tag
    success_url = reverse_lazy('calendar', args=(0,))


class IngredientUpdate(UpdateView):
    model = Ingredient
    form_class = IngredientModelForm


class IngredientCreate(CreateView):
    model = Ingredient
    form_class = IngredientModelForm

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()
        for tag in form.cleaned_data['tags']:
            self.object.tags.add(tag)
        return super(ModelFormMixin, self).form_valid(form)


class IngredientDetail(DetailView):
    model = Ingredient


class IngredientDelete(DeleteView):
    model = Ingredient
    success_url = reverse_lazy('calendar', args=(0,))


class IngredientList(ListView):
    model = Ingredient

    def get_context_data(self, **kwargs):
        context = super(IngredientList, self).get_context_data(**kwargs)
        context['ingredients'] = Ingredient.objects.all().annotate(num_dishes=Count('dish', distinct=True)).order_by('-num_dishes')
        return context


# From https://docs.djangoproject.com/en/1.9/ref/models/meta/#migrating-from-the-old-api
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


def model_json(request, model_name):
    model = apps.get_model('themenu', model_name.title())
    order_by = request.GET.get('order_by')

    # model_fields = list(model._meta.get_fields())
    model_fields = get_fields(model)
    base_query_set = model.objects.values(*[str(f) for f in model_fields])

    if order_by:
        base_query_set = base_query_set.order_by(order_by)

    tag_query_set = list(base_query_set)
    return JsonResponse(tag_query_set, safe=False)
