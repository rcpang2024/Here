from rest_framework import serializers
from ..models import User, Event, Notification, Comment
from datetime import datetime

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
    sender_photo = serializers.CharField(source='sender.profile_pic', read_only=True)
    event_name = serializers.CharField(source='event.event_name', read_only=True)
    class Meta:
        model = Notification
        fields = ['id', 'notification_type', 'recipient', 'sender', 'sender_username', 'sender_photo', 'timestamp', 'event', 'event_name']

class CommentModelSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    author_profilepic = serializers.CharField(source='author.profile_pic', read_only=True)
    replies = serializers.SerializerMethodField()
    mentioned_username = serializers.CharField(source='mentioned_user.username', read_only=True)
    formatted_timestamp = serializers.SerializerMethodField()
    class Meta:
        model = Comment
        fields = ['id', 'author', 'author_username', 'author_profilepic', 'event', 'message', 'timestamp', 'parent', 'replies', 'mentioned_user', 'mentioned_username', 'formatted_timestamp']

    def get_replies(self, obj):
        """Retrieve replies to a comment"""
        replies = obj.replies.all().order_by('timestamp')
        return CommentModelSerializer(replies, many=True).data
    
    def get_formatted_timestamp(self, obj):
        return obj.timestamp.strftime('%m-%d-%Y')