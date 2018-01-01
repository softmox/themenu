from __future__ import unicode_literals
import calendar
import random
from django.db import models
from django.db.models import Count, Min, Avg, Sum, Case, When, IntegerField, DateField, Q
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse, reverse_lazy
from datetime import date, datetime


def randcolor():
    return random.choice(Tag.TAG_COLORS)


class Team(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def get_absolute_url(self):
        return reverse('team-detail', args=[str(self.id)])

    def __str__(self):
        return self.name

    def common_ingredients(self):
        """Return a list ingredient objects,
        ordered by those the team most commonly uses"""

        ingredients = Ingredient.objects.filter(dish__meal__team=self).values("name", "id").distinct().annotate(num_meals=Count('dish__meal')).order_by('-num_meals')[:10]
        return ingredients

    def common_dishes(self):
        dishes = Dish.objects.filter(meal__team=self).values("name", "id").distinct().annotate(num_meals=Count('meal')).order_by('-num_meals')[:10]
        return dishes

    def cooked_dishes(self):
        dishes = Dish.objects.\
            annotate(cooked_meals=Sum(
                Case(
                    When(~Q(meal__team=self), then=0),
                    When(~Q(meal__meal_prep='cook'), then=0),
                    When(meal__course__prepared=True, then=1),
                    output_field=IntegerField()
                )
            ))\
            .filter(cooked_meals__gte=1)\
            .order_by('-cooked_meals')[:10]
        return dishes

    def eaten_dishes(self):
        dishes = Dish.objects.\
            annotate(eaten_meals=Sum(
                Case(
                    When(~Q(meal__team=self), then=0),
                    When(meal__course__eaten=True, then=1),
                    output_field=IntegerField()
                )
            ))\
            .filter(eaten_meals__gte=1)\
            .order_by('-eaten_meals')[:10]
        return dishes

    def prep_rate(self):
        prep = self.meal_set.filter(meal_prep='cook').aggregate(
            rate=Avg(
                Case(
                    When(course__prepared=False, then=0),
                    When(course__prepared=True, then=1),
                    output_field=IntegerField()
                )
            )
        )
        return int((prep['rate'] or 0) * 100)

    def eat_rate(self):
        eat = self.meal_set.filter(meal_prep='cook')\
        .aggregate(
            rate=Avg(
                Case(
                When(course__eaten=False, then=0),
                When(course__eaten=True, then=1),
                output_field=IntegerField()
                )
            )
        )
        return int((eat['rate'] or 0) * 100)

    def plan_rate(self):
        min_date = self.meal_set.aggregate(min_date=Min('date'))['min_date']
        if not min_date:
            days_planning = 1
        else:
            days_planning = (date.today() - min_date).days
        breakfasts = self.meal_set.filter(meal_type='breakfast').count()
        lunches = self.meal_set.filter(meal_type='lunch').count()
        dinners = self.meal_set.filter(meal_type='dinner').count()
        snacks = self.meal_set.filter(meal_type='snack').count()
        all_meals = breakfasts + lunches + dinners + snacks
        planning = {}
        planning['breakfasts'] = breakfasts*100/days_planning
        planning['lunches'] = lunches*100/days_planning
        planning['dinners'] = dinners*100/days_planning
        planning['snacks'] = snacks*100/days_planning
        planning['all'] = (breakfasts + lunches + dinners + snacks) * 100/(days_planning * 4)
        return planning


class MyUser(models.Model):
    user = models.OneToOneField(User)
    team = models.ForeignKey(Team, null=True, blank=True)

    def __str__(self):
        return self.user.username


class Tag(models.Model):
    """Any label for a Menu, Dish, or Ingredient"""
    class Meta:
        ordering = ['name']

    def get_absolute_url(self):
        return reverse('tag-detail', args=[str(self.id)])

    TAG_COLORS = [
        'Wheat', 'PeachPuff', 'YellowGreen', 'RosyBrown', 'Peru',
        'Khaki', 'Salmon', 'LemonChiffon', 'Orange', 'Lavender', 'Tomato',
        'LightBlue', 'DarkSeaGreen', 'Pink'
    ]

    name = models.CharField(max_length=48)
    color = models.CharField(max_length=48, default=randcolor)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Some food thing in a dish"""
    class Meta:
        ordering = ['name']

    def get_absolute_url(self):
        return reverse('ingredient-detail', args=[str(self.id)])

    name = models.CharField(max_length=96, unique=True)
    tags = models.ManyToManyField(Tag, blank=True)

    def __unicode__(self):
        return self.name


class Dish(models.Model):
    """A single dish to be eaten as part of a meal"""
    class Meta:
        verbose_name_plural = "dishes"
        ordering = ['name']

    name = models.TextField()
    created_by = models.ForeignKey(MyUser)
    notes = models.TextField(null=True, blank=True)
    source = models.TextField(null=True, blank=True)
    recipe = models.TextField(null=True, blank=True)

    ingredients = models.ManyToManyField(Ingredient, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)

    def get_absolute_url(self):
        return reverse('dish-detail', args=[str(self.id)])

    def __unicode__(self):
        return self.name


class Quantity(models.Model):
    """An amount of an ingredient that goes into a meal

    Used in both the recipe display and grocery list"""

    UNITS = [
        ('oz ', 'ounce'),
        ('lb', 'pound'),
        ('mg', 'milligram'),
        ('g', 'gram'),
        ('kg ', 'kilogram'),

        ('c', 'cup'),
        ('gill', 'gill'),
        ('ml ', 'milliliter'),
        ('L', 'liter'),
        ('pt ', 'pint'),
        ('qt', 'quart'),
        ('gal', 'gallon'),
        ('tsp ', 'teaspoon'),
        ('tbsp', 'tablespoon'),
        ('fl oz', 'fluid ounces'),
        ('dash', 'dash'),
        ('pinch', 'pinch'),

        ('mm', 'millimeter'),
        ('cm', 'centimeter'),
        ('m', 'meter'),
        ('in', 'inch'),
        ('ft', 'foot'),


    ]

    unit = models.CharField(max_length=40, choices=UNITS, blank=True, null=True)

    # This is for things like a "medium size" tomato
    descriptor = models.CharField(max_length=256, blank=True, null=True)
    # This is a charfield, since it could be "3", "1.5", "1 2/3", "Two"
    value = models.CharField(max_length=40, blank=True, null=True)


class IngredientAmount(models.Model):
    """The intermediate model ingredients and quantities"""
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.ForeignKey(Quantity, on_delete=models.CASCADE)
    other_info = models.BooleanField(default=False)

    def __unicode__(self):
        return 'Ingredient: %s, Quantity: %s' % (self.ingredient, self.quantity)


class Meal(models.Model):
    """A collection of dishes to be eaten at one time"""
    class Meta:
        unique_together = ('date', 'meal_type', 'team')
        ordering = ['date']

    MEAL_TYPE_CHOICES = [
        ('breakfast', 'breakfast'),
        ('lunch', 'lunch'),
        ('dinner', 'dinner'),
        ('dessert', 'dessert'),
        ('snack', 'snack'),
        ('tapas', 'tapas'),
    ]

    MEAL_PREP_CHOICES = [
        ('cook', 'cook'),
        ('buy', 'buy'),
        ('leftover', 'leftover')
    ]

    dishes = models.ManyToManyField(Dish, blank=True, through='Course')
    tags = models.ManyToManyField(Tag, blank=True)
    meal_type = models.CharField(max_length=40, choices=MEAL_TYPE_CHOICES, null=True)
    meal_prep = models.CharField(max_length=40, choices=MEAL_PREP_CHOICES, null=True)
    date = models.DateField('meal date')
    team = models.ForeignKey(Team)

    def weeknum(self):
        _, weeknum, = self.date.isocalendar()
        return weeknum

    def weekday(self):
        _, _, weekdaynum = self.date.isocalendar()
        weekday = calendar.day_name[weekdaynum]
        return weekday

    def get_absolute_url(self):
        return reverse('calendar',
                       kwargs={'view_date': datetime.strftime(self.date, '%Y%m%d')})

    def __unicode__(self):
        return '{type} on {date}: {menu}'.format(type=self.meal_type,
                                                 date=self.date,
                                                 menu=', '.join(d.name for d in self.dishes.all())
                                                 )


class Course(models.Model):
    """The intermediate model connecting dishes and meals"""
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    prepared = models.BooleanField(default=False)
    eaten = models.BooleanField(default=False)

    def __unicode__(self):
        return 'Meal: %s, Dish: %s. prepared: %s, eaten: %s' % \
            (self.meal.id, self.dish.id, self.prepared, self.eaten)


class GroceryListItem(models.Model):
    """An item to buy, automatically populated from a new meal"""
    ingredient = models.ForeignKey(Ingredient)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)
    purchased = models.BooleanField(default=False)

    def __unicode__(self):
        return 'Ingredient: %s, %s, Purchased: %s' % \
            (self.ingredient.id, self.ingredient.name, self.purchased)


class RandomGroceryItem(models.Model):
    """For things like paper towels, random snacks..."""
    name = models.TextField()
    team = models.ForeignKey(Team)
    purchased = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse('grocery-list')

    def __unicode__(self):
        return 'Random Grocery Item: %s, Purchased: %s' % \
            (self.name, self.purchased)


class DishReview(models.Model):
    class Meta:
        unique_together = ('myuser', 'dish')

    FASTNESS_CHOICES = [(1, 'over 1 hour'), (2, '30 min - 1 hour'), (3, 'less than 30 min')]
    EASE_CHOICES = [(1, 'complicated'), (2, 'moderate'), (3, 'simple')]
    RESULTS_CHOICES = [(1, 'not so good'), (2, 'okay'), (3, 'tasty')]

    myuser = models.ForeignKey(MyUser)
    dish = models.ForeignKey(Dish)
    notes = models.TextField(null=True, blank=True)
    fastness = models.IntegerField(choices=FASTNESS_CHOICES, null=True, blank=True)
    ease = models.IntegerField(choices=EASE_CHOICES, null=True, blank=True)
    results = models.IntegerField(choices=RESULTS_CHOICES, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)
