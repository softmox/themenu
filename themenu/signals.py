from django.conf import settings
from django.db.models.signals import post_save

from django.dispatch import receiver

from .models import Course, GroceryListItem, MyUser


def get_course_ingredient_amounts(course):
    return (ingredient_amount for ingredient_amount
            in course.dish.ingredient_amounts.all())


def get_course_groceries(course):
    ingredient_ids = [ing_amt.id for ing_amt in get_course_ingredient_amounts(course)]
    return GroceryListItem.objects.filter(course=course, ingredient_amount__in=ingredient_ids)


@receiver(post_save, sender=Course)
def notify_course_post_save(sender, **kwargs):
    course = kwargs['instance']
    update_fields = kwargs['update_fields'] or ''
    # Only create groceries for "cook" type meals
    if course.meal.meal_prep != 'cook':
        return

    if kwargs['created'] is True:
        # Make new ones
        for ing_amt in get_course_ingredient_amounts(course):
            try:
                GroceryListItem.objects.get(course=course, ingredient_amount=ing_amt)
            except GroceryListItem.DoesNotExist:
                GroceryListItem(course=course, ingredient_amount=ing_amt).save()
    else:
        if 'eaten' in update_fields or 'prepared' in update_fields:
            get_course_groceries(course).update(purchased=True)
            return

        # Delete the grocery items for this course
        new_grocery_id_list = []
        for ing_amt in get_course_ingredient_amounts(course):
            try:
                GroceryListItem.objects.get(course=course, ingredient_amount=ing_amt)
            except GroceryListItem.DoesNotExist:
                g = GroceryListItem(course=course, ingredient_amount=ing_amt)
                g.save()
                # Keep track of the ones we just added
                new_grocery_id_list.append(g.id)
        groceries_to_delete = GroceryListItem.objects.filter(course=course, purchased=False).exclude(id__in=new_grocery_id_list)

        groceries_to_delete.delete()


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def add_myuser(sender, instance, created, **kwargs):
    if created:
        MyUser.objects.create(user=instance)
