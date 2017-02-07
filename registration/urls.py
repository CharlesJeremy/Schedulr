from django.conf.urls import url
from django.contrib.auth import views as auth_views

from .views import register

urlpatterns = [
        url(r'^login/$', auth_views.login, name='login'),
        url(r'^logout/$', auth_views.logout, { 'next_page': '/' }, name='logout'),
        url(r'^register/$', register, name='register'),
]
