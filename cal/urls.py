from django.conf.urls import url

from . import views

urlpatterns = [
        url(r'^$', views.index, name='index'),
        url(r'^get_event_feed$', views.get_event_feed, name='get_event_feed'),
        url(r'^add_course$', views.add_course, name='add_course'),
        url(r'^add_event$', views.add_event, name='add_event'),
]
