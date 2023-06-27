from django.db import models
from django.forms import ValidationError

# Create your models here.
class User(models.Model):
    USER_TYPE = {
        ('individual', 'individual'),
        ('organization', 'organization')
    }
    username = models.CharField(max_length=100, unique=True, default='')
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100, unique=True) # In the future update to EmailField
    phone_number = models.CharField(max_length=25, unique=True)
    list_of_followers = models.ManyToManyField('self', symmetrical=False, related_name='following', blank=True)
    list_of_following = models.ManyToManyField('self', symmetrical=False, related_name='followers', blank=True)
    user_type = models.CharField(max_length=100, choices=USER_TYPE, default='individual')
    created_events = models.ManyToManyField('Event', related_name='creators', blank=True)
    attending_events = models.ManyToManyField('Event', related_name='attending', blank=True)

    # Method to dynamically set the max_length of the created_events list
    def created_events_max_length(self):
        if self.user_type == 'individual':
            return 1
        elif self.user_type == 'organization':
            return 3
        else:
            raise ValidationError('Invalid User Type')
        
    # Checks if the length of the created_events field is longer than what is allowed
    def validate_created_events_max_length(self):
        max_length = self.created_events_max_length()
        if self.created_events.count() > max_length:
            raise ValidationError(f'Upgrade to create more events')
        
    def save(self, *args, **kwargs):
        self.full_clean()  # Validate the model
        if not self.id:
            # Set the ID before saving if it's a new instance
            self.id = self._meta.model.objects.all().order_by("-id").first().id + 1
        super().save(*args, **kwargs)

class Event(models.Model):
    creation_user = models.ForeignKey(User, related_name='events', on_delete=models.CASCADE)
    event_name = models.CharField(max_length=200, default='')
    event_description = models.TextField(blank=True)
    location = models.TextField()
    date = models.DateTimeField(auto_now=True)
    list_of_attendees = models.ManyToManyField(User, blank=True)

    # Method to dynamically set the max_length of the list_of_attendees list
    def list_of_attendees_max_length(self):
        if self.creation_user.user_type == 'individual':
            return 8
        elif self.creation_user.user_type == 'organization':
            return 100
        else:
            raise ValidationError('Invalid User Type')
        
    # Checks if the length of the list_of_attendees field is longer than what is allowed
    def validate_list_of_attendees_max_length(self):
        max_length = self.list_of_attendees_max_length()
        if self.list_of_attendees.count() > max_length:
            raise ValidationError(f'Upgrade to let more people follow your event')
    
    # Saves the object first and then validates
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.full_clean()
