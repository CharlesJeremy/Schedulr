from django.conf.urls import url

from . import views

urlpatterns = [
        url(r'^$', views.index, name='index'),
        url(r'^get_event_feed$', views.get_event_feed, name='get_event_feed'),
        url(r'^add_event$', views.add_event, name='add_event'),
        url(r'^get_sections$', views.get_sections_for_course, name='get_sections'),
        url(r'^add_sections$', views.add_sections, name='add_sections'),
        url(r'^delete_event/(?P<event_id>\d+)$', views.delete_event, name='delete_event'),
        url(r'^edit_event_abs/(?P<event_id>\d+)$', views.edit_event_abs, name='edit_event_abs'),
        url(r'^edit_event_rel/(?P<event_id>\d+)$', views.edit_event_rel, name='edit_event_rel'),
]
