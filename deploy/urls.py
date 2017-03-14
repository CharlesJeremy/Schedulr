from django.conf import settings
from django.conf.urls import url

from . import views


urlpatterns = []
if not settings.DEBUG:
    urlpatterns.append(url(r'^$', views.deploy, name='deploy'))

