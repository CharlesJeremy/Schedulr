from django.conf.urls import url

from . import views

urlpatterns = [
        url(r'^$', views.index, name='index'),
        url(r'^get_event_feed$', views.get_event_feed, name='get_event_feed'),
]
