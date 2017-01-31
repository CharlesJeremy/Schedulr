from django.contrib import admin
from .models import Event


class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'start_time', 'end_time')
    ordering = ('start_time',)


admin.site.register(Event, EventAdmin)
