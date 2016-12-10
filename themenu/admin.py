from django.contrib import admin

from .models import Tag, Ingredient, Dish, Menu, Meal

# class GameAdmin(admin.ModelAdmin):
#     readonly_fields = ('started_date', 'unique_id')

admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(Dish)
admin.site.register(Menu)
admin.site.register(Meal)
