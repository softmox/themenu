from django.contrib import admin

from .models import Tag, Ingredient, Dish, Meal, Course

# class GameAdmin(admin.ModelAdmin):
#     readonly_fields = ('started_date', 'unique_id')


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
# admin.site.register(Course)
