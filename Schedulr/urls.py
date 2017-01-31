"""Schedulr URL Configuration

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
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.http.response import HttpResponseRedirect

admin.site.site_header = settings.ADMIN_SITE_HEADER

urlpatterns = [
    url(r'^$', lambda r: HttpResponseRedirect('cal/')),
    url(r'^cal/', include('cal.urls', namespace='cal')),
    url(r'^accounts/', include('registration.urls', namespace='registration')),
    url(r'^admin/', admin.site.urls),
    url(r'^_nested_admin/', include('nested_admin.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
# TODO(zhangwen): serving static asset--only for development.
