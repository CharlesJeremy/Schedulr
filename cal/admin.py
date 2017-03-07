from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Event, SmartSchedulingPrefs


class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'start_time', 'end_time')
    ordering = ('start_time',)


class SmartSchedulingPrefsInline(admin.StackedInline):
    model = SmartSchedulingPrefs


class SchedulrUserAdmin(UserAdmin):
    inlines = [ SmartSchedulingPrefsInline ]


admin.site.register(Event, EventAdmin)

admin.site.unregister(User)
admin.site.register(User, SchedulrUserAdmin)
