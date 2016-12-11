from django.db import models
import calendar
# from datetime import date
# from django.contrib.auth.models import User


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

    SCORE_CHOICES = [(1, 'one star'), (2, 'two stars'), (3, 'three stars')]

    name = models.TextField()
    notes = models.TextField(null=True, blank=True)
    source = models.TextField(null=True, blank=True)
    recipe = models.TextField(null=True, blank=True)
    # Scores to rate the dishes on
    speed = models.IntegerField(choices=SCORE_CHOICES, default=1, null=True)
    complexity = models.IntegerField(choices=SCORE_CHOICES, default=1, null=True)
    results = models.IntegerField(choices=SCORE_CHOICES, default=1, null=True)

    ingredients = models.ManyToManyField(Ingredient, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)

    def __unicode__(self):
        return 'Dish: %s' % self.name


class Meal(models.Model):
    '''A collection of dishes to be eaten at one time'''
    class Meta:
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

    def weeknum(self):
        _, weeknum, = self.date.isocalendar()
        return weeknum

    def weekday(self):
        _, _, weekdaynum = self.date.isocalendar()
        weekday = calendar.day_name[weekdaynum]
        return weekday

    def __unicode__(self):
        return '{type} on {date}: {menu}'.format(type=self.meal_type,
                                                 date=self.date,
                                                 menu=','.join(d.name for d in self.dishes.all())
                                                 )


class Course(models.Model):
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    prepared = models.BooleanField(default=False)
    eaten = models.BooleanField(default=False)
