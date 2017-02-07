from django.conf.urls import url
from django.contrib.auth import views as auth_views

from .views import RegisterView

urlpatterns = [
        url(r'^login/$', auth_views.login, name='login'),
        url(r'^logout/$', auth_views.logout, { 'next_page': '/' }, name='logout'),
        url(r'^register/$', RegisterView.as_view(), name='register'),
]
