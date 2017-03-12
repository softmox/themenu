from django.contrib import admin

from .models import (
    Tag,
    Ingredient,
    Dish,
    Meal,
    Course,
    MyUser,
    Team,
    RandomGroceryItem
)


class CourseInline(admin.TabularInline):
    model = Course
    extra = 1


class DishAdmin(admin.ModelAdmin):
    inlines = (CourseInline,)


class MealAdmin(admin.ModelAdmin):
    inlines = (CourseInline,)


admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(Dish, DishAdmin)
admin.site.register(Meal, MealAdmin)
admin.site.register(MyUser)
admin.site.register(Team)
admin.site.register(RandomGroceryItem)
