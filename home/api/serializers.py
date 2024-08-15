from rest_framework import serializers
from ..models import User, Event, Notification

class UserModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class EventModelSerializer(serializers.ModelSerializer):
    # location = serializers.SerializerMethodField()
    creation_user_username = serializers.CharField(source='creation_user.username', read_only=True)
    class Meta:
        model = Event
        fields = ['id', 'creation_user', 'creation_user_username', 'event_name', 'event_description', 'location_addr', 'location_point', 'date', 'list_of_attendees']

    # def get_location(self, obj):
    #     if obj.location:
    #         return {'latitude': obj.location.y, 'longitude': obj.location.x}
    #     return None

class NotificationModelSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    class Meta:
        model = Notification
        fields = ['id', 'notification_type', 'recipient', 'sender', 'sender_username', 'timestamp']