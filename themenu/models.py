import calendar
import random
from django.db import models
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


class MyUser(models.Model):
    user = models.OneToOneField(User)
    team = models.ForeignKey(Team, null=True, blank=True)

    def __str__(self):
        return self.user.username


class Tag(models.Model):
    '''Any label for a Menu, Dish, or Ingredient'''
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
    '''Some food thing in a dish'''
    class Meta:
        ordering = ['name']

    def get_absolute_url(self):
        return reverse('ingredient-detail', args=[str(self.id)])

    name = models.CharField(max_length=96, unique=True)
    tags = models.ManyToManyField(Tag, blank=True)

    def __unicode__(self):
        return self.name


class Dish(models.Model):
    '''A collection of dishes to be eaten at one time'''
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


class Meal(models.Model):
    '''A collection of dishes to be eaten at one time'''
    class Meta:
        unique_together = ('date', 'meal_type')
        ordering = ['date']

    MEAL_TYPE_CHOICES = [
        ('breakfast', 'breakfast'),
        ('lunch', 'lunch'),
        ('dinner', 'dinner'),
        ('dessert', 'dessert'),
        ('snack', 'snack'),
        ('tapas', 'tapas'),
    ]
    dishes = models.ManyToManyField(Dish, blank=True, through='Course')
    tags = models.ManyToManyField(Tag, blank=True)
    meal_type = models.CharField(max_length=40, choices=MEAL_TYPE_CHOICES, null=True)
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
            kwargs={
                'view_date': datetime.strftime(self.date, '%Y%m%d')
            }
        )

    def __unicode__(self):
        return '{type} on {date}: {menu}'.format(type=self.meal_type,
                                                 date=self.date,
                                                 menu=', '.join(d.name for d in self.dishes.all())
                                                 )


class Course(models.Model):
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    prepared = models.BooleanField(default=False)
    eaten = models.BooleanField(default=False)

    def __unicode__(self):
        return 'Meal: %s, Dish: %s. prepared: %s, eaten: %s' % \
            (self.meal.id, self.dish.id, self.prepared, self.eaten)


class GroceryListItem(models.Model):
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
    notes = models.CharField(max_length=1000)
    fastness = models.IntegerField(choices=FASTNESS_CHOICES, null=True, blank=True)
    ease = models.IntegerField(choices=EASE_CHOICES, null=True, blank=True)
    results = models.IntegerField(choices=RESULTS_CHOICES, null=True, blank=True)
