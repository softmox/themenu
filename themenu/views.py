import json
from collections import defaultdict, OrderedDict
from itertools import chain
from datetime import timedelta, date, datetime

from django.apps import apps
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse, reverse_lazy
from django.core.exceptions import PermissionDenied

from django.views.generic.edit import CreateView, ModelFormMixin
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView, DeleteView


from django.views.decorators.http import require_http_methods
from django.shortcuts import redirect
from django.contrib import messages

from django.db.models import Count, Avg

# from registration.views import RegistrationView

from themenu.models import (
    Team, MyUser, Tag,
    Ingredient, IngredientAmount, Dish, Meal,
    Course, GroceryListItem,
    RandomGroceryItem, DishReview
)

from themenu.forms import (
    DishModelForm,
    DishForm,
    MealModelForm,
    TagModelForm,
    IngredientModelForm,
    IngredientSearchForm,
)


def index(request):
    return redirect('calendar', view_date=datetime.strftime(date.today(), '%Y%m%d'))


def scores(request):
    fast_dishes = Dish.objects.annotate(avg_speed=Avg('dishreview__fastness'))\
        .filter(avg_speed__gte=2.5).order_by('-avg_speed')
    tasty_dishes = Dish.objects.annotate(avg_results=Avg('dishreview__results'))\
        .filter(avg_results__gte=2.5).order_by('-avg_results')
    easy_dishes = Dish.objects.annotate(avg_ease=Avg('dishreview__ease'))\
        .filter(avg_ease__gte=2.5).order_by('-avg_ease')

    hall_of_fame = []
    for dish in fast_dishes:
        if dish in tasty_dishes and dish in easy_dishes:
            hall_of_fame.append(dish)

    context = {
        'fast_dishes': fast_dishes,
        'tasty_dishes': tasty_dishes,
        'easy_dishes': easy_dishes,
        'perfect_dishes': hall_of_fame,
    }
    return render(request, 'themenu/scores.html', context)


def grocery_list(request):
    """Logic for populating the grocery list

    Much has to do with the fact that we have one item for each meal
    that uses the same ingredient.
    This is so that on the shopping list, you can see which meals you are
    getting an item for"""
    def _get_meal_groceries(team):
        """Fetches the future meals for a team, unpurchased first"""
        return GroceryListItem.objects.filter(course__meal__team=team)\
                                      .filter(course__meal__date__gte=date.today())\
                                      .order_by('purchased', 'course__meal__date')

    def _get_random_groceries(team):
        """Returns a queryset with all unpurchased RandomGroceryItems"""
        return RandomGroceryItem.objects.filter(team=team)\
                                        .filter(purchased=False)\
                                        .order_by('purchased')

    team = request.user.myuser.team
    if not team:
        return HttpResponseRedirect(reverse('team-list'))
        # redirect to a team registration page
        # if you don't have a team, you can't plan meals
        # so why would you need a grocery list

    grocery_list = _get_meal_groceries(team)

    # Using defaultdict to group same named ingredients together
    ingredient_grocery_list = defaultdict(lambda: ([], []))

    # This variables will end up as a list with 5-tuples:
    # (u'frozen berries',  <- The name of the ingredient
    #   [<GroceryListItem: IngredientAmount: 28, frozen berries, Purchased: False>,
    #    <GroceryListItem: IngredientAmount: 28, frozen berries, Purchased: False>],
    #  '1/4 cup, 1 bowl'  <- a string of the amounts of the ingredients
    #  False,      <- True/False if they have all been purchased already
    #  '245,267')  <- ids of the GroceryListItems as a string list for html data
    # The whole GroceryListItem model is included so the template can get the
    # dish name, meal type, number of meals, and meal date

    for grocery_item in grocery_list:
        key = grocery_item.ingredient_amount.ingredient.name
        amount = grocery_item.ingredient_amount.amount
        ingredient_grocery_list[key][0].append(grocery_item)
        ingredient_grocery_list[key][1].append(amount)
    # Add the fourth and fifth items to the tuples:
    # a bool if all groceries have been purchased, and
    # a comma separated string of grocery ids (to update all at once)
    mark_all_purchased = [
        (ingredient_name,                                  # name (string)
         ', '.join(a if a else 'N/A' for a in amount_list),  # ids_string
         grocery_items,                               # list of models
         all(g.purchased for g in grocery_items),     # purchased bool
         ','.join(str(g.id) for g in grocery_items))  # ids_string
        for ingredient_name, (grocery_items, amount_list) in ingredient_grocery_list.items()
    ]
    # Sort the (ingredient, [grocery1,grocery2,..], purchased) tuples with
    # ones where everything has been purchased last
    sorted_items = sorted(mark_all_purchased, key=lambda x: x[2])

    random_grocery_list = _get_random_groceries(team)
    context = {
        'ingredient_grocery_list': sorted_items,
        'random_grocery_list': random_grocery_list,
    }
    return render(request, 'themenu/grocery_list.html', context)


def calendar(request, view_date):
    parsed_date = datetime.strptime(str(view_date), '%Y%m%d')
    team = request.user.myuser.team

    if not team:
        return HttpResponseRedirect(reverse('team-list'))
        # redirect to a team register page
        # if you don't have a team, you can't plan meals

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
        # prettymonday = monday.strftime('%d %B, %Y')
        return monday

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

    def save_grocery(grocery, checked_value):
        grocery.purchased = checked_value
        grocery.save(update_fields=['purchased'])

    posted_data = json.loads(request.body)
    id_list = [int(item) for item in str(posted_data['groceryId']).split(',')]
    checked_value = posted_data['checked']
    if posted_data['groceryType'] == 'meal':
        print(posted_data)

        grocery_list = GroceryListItem.objects.filter(id__in=id_list)
        # Now save each one individually
        for grocery in grocery_list:
            save_grocery(grocery, checked_value)
    elif posted_data['groceryType'] == 'random':
        print(posted_data)
        grocery = get_object_or_404(RandomGroceryItem, id=posted_data['groceryId'])
        save_grocery(grocery, checked_value)
    else:
        JsonResponse({"OK": False})

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
        comma_separated_items = form.data['name']
        team = get_object_or_404(Team, myuser=self.request.user.myuser)
        if ',' not in comma_separated_items:
            # User has only added one item, no commas
            obj = form.save(commit=False)
            obj.team = team
            obj.save()
            return super(RandomGroceryItemCreate, self).form_valid(form)
        else:
            # Otherwise, split the single string,
            # Saving one new grocery item per name
            item_names = [item.strip() for item in comma_separated_items.split(",")]
            new_object = None
            for name in item_names:
                new_object = RandomGroceryItem(name=name, team=team)
                new_object.save()
            return HttpResponseRedirect(new_object.get_absolute_url())


class DishDetail(DetailView):
    model = Dish

    def get_context_data(self, **kwargs):
        context = super(DishDetail, self).get_context_data(**kwargs)
        this_dish = self.object
        try:
            context['user_review'] = this_dish.dishreview_set.filter(myuser=self.request.user.myuser).first()
            context['other_reviews'] = this_dish.dishreview_set.exclude(myuser=self.request.user.myuser)
        except AttributeError:  # Anonymous user
            pass
        return context


class DishUpdate(UpdateView):
    model = Dish
    form_class = DishModelForm

    def get_context_data(self, **kwargs):
        context = super(DishUpdate, self).get_context_data(**kwargs)
        # If we need to add extra items to what passes to the template
        # context['now'] = timezone.now()
        return context

    def get_object(self, *args, **kwargs):
        """Overridden to allow only team members to change dish"""
        obj = super(DishUpdate, self).get_object(*args, **kwargs)
        if not obj.created_by.team == self.request.user.myuser.team:
            # Either return back to previous page, or to home if browser is stubborn
            messages.error(self.request, 'You do not have permission to alter this object')
            messages.error(self.request, "You can only alter your team's objects")
            # return HttpResponseRedirect(self.request.META.get('HTTP_REFERER', '/'))
            raise PermissionDenied
        return obj


class DishCreate(CreateView):
    model = Dish
    form_class = DishForm

    def form_valid(self, form):
        obj = form.save(commit=False)
        myuser = get_object_or_404(MyUser, user=self.request.user)
        obj.created_by = myuser
        obj.save()
        form.save_m2m()
        return HttpResponseRedirect(obj.get_absolute_url())


def dish_create(request):
    def save_dish(form):
        new_dish = form.save(commit=False)
        # import ipdb; ipdb.set_trace()
        # form_data = form.data
        # dfd = dict(form_data)
        # ias = zip(dfd['ingredient'], dfd['amount'])
        ias = zip(form.data.getlist('ingredient'), form.data.getlist('amount'))
        used_ing_amts = []
        for ia in ias:
            if not ia[0]:  # no ingredient, blank
                continue
            ingredient = Ingredient.objects.get(pk=int(ia[0]))
            new_ia, created = IngredientAmount.objects.get_or_create(ingredient=ingredient,
                                                                     amount=ia[1])
            used_ing_amts.append(new_ia)

        # dfd.pop('ingredient')
        # dfd.pop('amount')
        # dfd.pop('csrfmiddlewaretoken')
        # new_dish = Dish(**dfd)
        myuser = get_object_or_404(MyUser, user=request.user)
        new_dish.created_by = myuser
        new_dish.save()
        for ia in used_ing_amts:
            new_dish.ingredient_amounts.add(ia)
        form.save_m2m()  # Save the list of tags, another M2M

        return new_dish

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = DishForm(request.POST)
        # check whether it's valid:
        print('DISH CREATE')
        print(form.data)
        print(form.data.getlist('ingredient'))

        if form.is_valid():
            # redirect to a new URL:
            new_dish = save_dish(form)
            return HttpResponseRedirect(reverse('dish-detail', kwargs={'pk': new_dish.id}))
        else:
            print('FORM INVALID')
            print(form.errors)

    # if a GET (or any other method) we'll create a blank form
    else:
        form = DishForm()

    return render(request, 'themenu/dish_form.html', {'form': form})


class DishDelete(DeleteView):
    model = Dish
    success_url = reverse_lazy('index')

    def get_object(self, *args, **kwargs):
        """Overridden to allow only team members to delete dish"""
        obj = super(DishDelete, self).get_object(*args, **kwargs)
        if not obj.created_by.team == self.request.user.myuser.team:
            messages.error(self.request, 'You do not have permission to alter this object')
            messages.error(self.request, "You can only alter your team's objects")
            raise PermissionDenied
        return obj


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


class TeamList(ListView):
    model = Team


def team_join(request, **kwargs):
    team_id = kwargs['pk']
    team = Team.objects.filter(id=team_id).first()
    myuser = request.user.myuser
    myuser.team = team
    myuser.save()
    return HttpResponseRedirect(reverse('team-detail', kwargs={'pk': team_id}))

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
    def get_object(self, *args, **kwargs):
        """Overridden to allow only team members to change"""
        obj = super(MealDelete, self).get_object(*args, **kwargs)
        if not obj.team == self.request.user.myuser.team:
            # Either return back to previous page, or to home if browser is stubborn
            messages.error(self.request, 'You do not have permission to alter this object')
            messages.error(self.request, "You can only alter your team's objects")
            # return HttpResponseRedirect(self.request.META.get('HTTP_REFERER', '/'))
            raise PermissionDenied
        return obj

    model = Meal
    success_url = reverse_lazy('index')


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

    def get_object(self, *args, **kwargs):
        """Overridden to allow only team members to change"""
        obj = super(MealUpdate, self).get_object(*args, **kwargs)
        if not obj.team == self.request.user.myuser.team:
            messages.error(self.request, 'You do not have permission to alter this object')
            messages.error(self.request, "You can only alter your team's objects")
            raise PermissionDenied
        return obj

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
        # TODO: https://github.com/goobers/themenu/issues/90
        # context['ingredients'] = tag_ing.annotate(num_dishes=Count('dish')).order_by('-num_dishes')[:15]
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
    success_url = reverse_lazy('index')


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

    def get_context_data(self, **kwargs):
        context = super(IngredientDetail, self).get_context_data(**kwargs)
        context['dish_set'] = Dish.objects.filter(ingredient_amounts__ingredient=self.object)
        return context


class IngredientDelete(DeleteView):
    model = Ingredient
    success_url = reverse_lazy('index')


class IngredientList(ListView):
    model = Ingredient

    def get_context_data(self, **kwargs):
        context = super(IngredientList, self).get_context_data(**kwargs)
        context['ingredient_amounts'] = IngredientAmount.objects.all().annotate(num_dishes=Count('dish', distinct=True)).order_by('-num_dishes')
        # Form is to search for ingredient details
        context['form'] = IngredientSearchForm
        return context

    def post(self, request, *args, **kwargs):
        ingredient_id = request.POST.get('name')
        return HttpResponseRedirect(reverse('ingredient-detail',
                                    args=(ingredient_id,)))


class DishReviewCreate(CreateView):
    model = DishReview
    fields = ['notes', 'fastness', 'ease', 'results']

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.myuser = get_object_or_404(MyUser, user=self.request.user)
        obj.dish = get_object_or_404(Dish, id=self.kwargs['dish_id'])
        obj.save()
        form.save_m2m()
        return HttpResponseRedirect(reverse('dish-detail', kwargs={'pk': self.kwargs['dish_id']}))


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
