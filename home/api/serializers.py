from rest_framework import serializers
from ..models import User, Event, Notification

class UserModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class EventModelSerializer(serializers.ModelSerializer):
    # location = serializers.SerializerMethodField()
    class Meta:
        model = Event
        fields = '__all__'

    # def get_location(self, obj):
    #     if obj.location:
    #         return {'latitude': obj.location.y, 'longitude': obj.location.x}
    #     return None

class NotificationModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'