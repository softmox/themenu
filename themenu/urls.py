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
from themenu import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^admin/', admin.site.urls),
    url(r'^calendar/(?P<offset>[\-\d]+)/?$', views.calendar, name='calendar'),
    url(r'^courseupdate/?$', views.course_update, name='course-update'),
    url(r'^groceryupdate/?$', views.grocery_update, name='grocery-update'),
    url(r'^grocery_list/$', views.grocery_list, name='grocery-list'),

    # Generic dish views (with select2 widgets)
    url(r'^dishes/create/$', views.DishCreateView.as_view(), name='dish-create'),
    url(r'^dishes/(?P<pk>[\d]+)/update/$', views.DishUpdateView.as_view(), name='dish-update'),
    url(r'^dishes/(?P<pk>[\d]+)/?$', views.DishDetailView.as_view(), name='dish-detail'),

    # Generic meal views (with select2 widgets)
    url(r'^meals/create/?$', views.MealCreateView.as_view(), name='meal-create'),
    url(r'^meals/(?P<pk>[\d]+)/update/?$', views.MealUpdateView.as_view(), name='meal-update'),
    url(r'^meals/(?P<pk>[\d]+)/delete/?$', views.MealDeleteView.as_view(), name='meal-delete'),
    url(r'^meals/(?P<pk>[\d]+)/?$', views.MealDetailView.as_view(), name='meal-detail'),

    # Generic tag views
    url(r'^tags/$', views.TagListView.as_view(), name='tag-list'),
    url(r'^tags/create/?$', views.TagCreateView.as_view(), name='tag-create'),
    url(r'^tags/(?P<pk>[\d]+)/update/?$', views.TagUpdateView.as_view(), name='tag-update'),
    url(r'^tags/(?P<pk>[\d]+)/?$', views.TagDetailView.as_view(), name='tag-detail'),

    url(r'^api/(?P<model_name>[\w]+)/?$', views.model_json_view, name='model-json'),
    url(r'^select2/', include('django_select2.urls')),
]
