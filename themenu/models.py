from django.db import models
# from django.contrib.auth.models import User

SCORE_CHOICES = [(1, 'one star'), (2, 'two stars'), (3, 'three stars')]
MEAL_TYPE_CHOICES = [
    ('breakfast', 'breakfast'),
    ('lunch', 'lunch'),
    ('dinner', 'dinner'),
    ('dessert', 'dessert'),
    ('snack', 'snack'),
    ('tapas', 'tapas'),
]


class Tag(models.Model):
    '''Any label for a Menu, Dish, or Ingredient'''
    name = models.TextField()

    def __unicode__(self):
        return 'Tag: %s' % self.name


class Ingredient(models.Model):
    '''Some food thing in a dish'''
    name = models.TextField()
    tags = models.ManyToManyField(Tag)

    def __unicode__(self):
        return 'Ingredient: %s' % self.name


class Dish(models.Model):
    '''A collection of dishes to be eaten at one time'''
    class Meta:
        verbose_name_plural = "dishes"

    name = models.TextField()
    notes = models.TextField(null=True, blank=True)
    source = models.TextField(null=True, blank=True)
    recipe = models.TextField(null=True, blank=True)
    # Scores to rate the dishes on
    speed = models.IntegerField(choices=SCORE_CHOICES, default=1, null=True)
    complexity = models.IntegerField(choices=SCORE_CHOICES, default=1, null=True)
    results = models.IntegerField(choices=SCORE_CHOICES, default=1, null=True)

    ingredients = models.ManyToManyField(Ingredient)
    tags = models.ManyToManyField(Tag)

    def __unicode__(self):
        return 'Dish: %s' % self.name


class Menu(models.Model):
    '''A collection of dishes to be eaten at one time'''
    name = models.TextField(null=True, blank=True)
    dishes = models.ManyToManyField(Dish, blank=True)
    tags = models.ManyToManyField(Tag)

    def __unicode__(self):
        return 'Menu: %s' % self.name


class DayPlan(models.Model):
    '''A collection of Menus (meals) for a day'''
    date = models.DateField('plan date')

    def __unicode__(self):
        return 'Day plan for %s' % self.date


class Meal(models.Model):
    '''A collection of dishes to be eaten at one time'''
    menu = models.ForeignKey(Menu)
    prepared = models.BooleanField(default=False)
    eaten = models.BooleanField(default=False)
    meal_type = models.CharField(max_length=40, choices=MEAL_TYPE_CHOICES, null=True)
    dayplan = models.ForeignKey(DayPlan)

    def __unicode__(self):
        return '{type} on {date}: {menu}'.format(type=self.meal_type,
                                                 date=self.dayplan.date,
                                                 menu=self.menu.name)
