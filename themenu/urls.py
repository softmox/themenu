"""themenu URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from themenu import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^calendar/(?P<view_date>[\-\d]+)/?$', views.calendar, name='calendar'),
    url(r'^courseupdate/?$', views.course_update, name='course-update'),
    url(r'^groceryupdate/?$', views.grocery_update, name='grocery-update'),
    url(r'^grocery_list/$', views.grocery_list, name='grocery-list'),
    url(r'^scores/$', views.scores, name='scores'),

    # login / account views
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),
    url(r'^admin/', admin.site.urls),
    url(r'^', include('registration.backends.simple.urls')),
    url(r'^profile/(?P<pk>[\d]+)/?$', views.MyUserDetail.as_view(),
    name='user-profile'),

    # team views
    url(r'^teams/create/$', views.TeamCreate.as_view(), name='team-create'),
    url(r'^teams/(?P<pk>[\d]+)/?$', views.TeamDetail.as_view(), name='team-detail'),

    # Generic dish views (with select2 widgets)
    url(r'^dishes/create/$', views.DishCreate.as_view(), name='dish-create'),
    url(r'^dishes/(?P<pk>[\d]+)/update/$', views.DishUpdate.as_view(), name='dish-update'),
    url(r'^dishes/(?P<pk>[\d]+)/delete/?$', views.DishDelete.as_view(), name='dish-delete'),
    url(r'^dishes/(?P<pk>[\d]+)/?$', views.DishDetail.as_view(), name='dish-detail'),
    url(r'^dishes/search/?$', views.dish_search, name='dish-search'),

    # Generic meal views (with select2 widgets)
    url(r'^meals/create/?$', views.MealCreate.as_view(), name='meal-create'),
    url(r'^meals/(?P<pk>[\d]+)/update/?$', views.MealUpdate.as_view(), name='meal-update'),
    url(r'^meals/(?P<pk>[\d]+)/delete/?$', views.MealDelete.as_view(), name='meal-delete'),
    url(r'^meals/(?P<pk>[\d]+)/?$', views.MealDetail.as_view(), name='meal-detail'),

    # Generic tag views
    url(r'^tags/$', views.TagList.as_view(), name='tag-list'),
    url(r'^tags/create/?$', views.TagCreate.as_view(), name='tag-create'),
    url(r'^tags/(?P<pk>[\d]+)/update/?$', views.TagUpdate.as_view(), name='tag-update'),
    url(r'^tags/(?P<pk>[\d]+)/delete/?$', views.TagDelete.as_view(), name='tag-delete'),
    url(r'^tags/(?P<pk>[\d]+)/?$', views.TagDetail.as_view(), name='tag-detail'),

    # Generic ingredient views
    url(r'^ingredients/$', views.IngredientList.as_view(), name='ingredient-list'),
    url(r'^ingredients/create/?$', views.IngredientCreate.as_view(), name='ingredient-create'),
    url(r'^ingredients/(?P<pk>[\d]+)/update/?$', views.IngredientUpdate.as_view(), name='ingredient-update'),
    url(r'^ingredients/(?P<pk>[\d]+)/delete/?$', views.IngredientDelete.as_view(), name='ingredient-delete'),
    url(r'^ingredients/(?P<pk>[\d]+)/?$', views.IngredientDetail.as_view(), name='ingredient-detail'),

    url(r'^randomgrocery/create/?$', views.RandomGroceryItemCreate.as_view(), name='random-grocery-create'),

    url(r'^api/(?P<model_name>[\w]+)/?$', views.model_json, name='model-json'),
    url(r'^select2/', include('django_select2.urls')),
]
