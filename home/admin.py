from django.contrib import admin
from .models import User, Event

class EventAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Check if it's a new event being created
            obj.save()  # Save the event to get the primary key assigned
            obj.creation_user.created_events.add(obj)  # Add the event to the created_events field
        else:
            obj.save()  # Save the event normally for existing events

# Register your models here.
admin.site.register(User)
# admin.site.register(Event)
admin.site.register(Event, EventAdmin)
