from rest_framework import status
from auth_backend import FirebaseAuthentication, SupabaseAuthentication
from ..models import User, Event, Notification
from .serializers import UserModelSerializer, EventModelSerializer, NotificationModelSerializer
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.http import JsonResponse
from django_ratelimit.decorators import ratelimit
import firebase_admin
from firebase_admin import auth
import requests
import json

# USER API ENDPOINTS

# For development purposes, not used in app itself
@api_view(['GET'])
@permission_classes([AllowAny])
def getNotifs(request):
    notifications = Notification.objects.all()
    serializer = NotificationModelSerializer(notifications, many=True)
    return Response(serializer.data)

# For development purposes, not used in app itself
@api_view(['GET'])
@permission_classes([AllowAny])
def getUsers(request):
    max_id = 3000
    users = User.objects.filter(id__lt=max_id)
    serializer = UserModelSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@authentication_classes([SupabaseAuthentication])
@permission_classes([IsAuthenticated])
def getUserByID(request, id):
    user = User.objects.get(id=id)
    serializer = UserModelSerializer(user, many=False)
    return Response(serializer.data)

@ratelimit(key='ip', rate='30/m', block=True)
@api_view(['GET'])
@authentication_classes([SupabaseAuthentication])
@permission_classes([IsAuthenticated])
def getUserByUsername(request, username):
    user = User.objects.get(username=username)
    serializer = UserModelSerializer(user, many=False)
    return Response(serializer.data)

@ratelimit(key='ip', rate='5/m', block=True)
@api_view(['GET'])
@authentication_classes([SupabaseAuthentication])
@permission_classes([IsAuthenticated])
def getUserByEmail(request, email):
    try:
        user = User.objects.get(email=email)
        serializer = UserModelSerializer(user, many=False)
        return Response(serializer.data)
    except:
        return Response("Too many requests. Try again later.", status=status.HTTP_429_TOO_MANY_REQUESTS)

# Returns the list of users that the user is following
@ratelimit(key='ip', rate='10/m', block=True)
@api_view(['GET'])
@authentication_classes([SupabaseAuthentication])
@permission_classes([IsAuthenticated])
def getFollowing(request, username):
    try:
        user = User.objects.get(username=username)
        following_users = user.list_of_following.all()
        serializer = UserModelSerializer(following_users, many=True)
        return Response(serializer.data)
    except:
        return Response("Too many requests. Try again later.", status=status.HTTP_429_TOO_MANY_REQUESTS)

# Returns the user's followers list
@ratelimit(key='ip', rate='10/m', block=True)
@api_view(['GET'])
@authentication_classes([SupabaseAuthentication])
@permission_classes([IsAuthenticated])
def getFollowers(request, username):
    try:
        user = User.objects.get(username=username)
        followers = user.list_of_followers.all()
        serializer = UserModelSerializer(followers, many=True)
        return Response(serializer.data)
    except:
        return Response("Too many requests. Try again later.", status=status.HTTP_429_TOO_MANY_REQUESTS)

# Returns the list of users who have requested to follow the user
@ratelimit(key='ip', rate='10/m', block=True)
@api_view(['GET'])
@authentication_classes([SupabaseAuthentication])
@permission_classes([IsAuthenticated])
def getFollowRequests(request, username):
    try:
        user = User.objects.get(username=username)
        followRequests = user.follow_requests.all()
        serializer = UserModelSerializer(followRequests, many=True)
        return Response(serializer.data)
    except:
        return Response("Too many requests. Try again later.", status=status.HTTP_429_TOO_MANY_REQUESTS)
    
@ratelimit(key='ip', rate='5/m', block=True)
@api_view(['GET'])
@authentication_classes([SupabaseAuthentication])
@permission_classes([IsAuthenticated])
def getBlockedList(request, username):
    try:
        user = User.objects.get(username=username)
        list_of_blocked = user.blocked_users.all()
        serializer = UserModelSerializer(list_of_blocked, many=True)
        return Response(serializer.data)
    except:
        return Response("Too many requests. Try again later.", status=status.HTTP_429_TOO_MANY_REQUESTS)

@ratelimit(key='ip', rate='50/m', block=True)
@api_view(['GET'])
@permission_classes([AllowAny])
def searchUsers(request):
    query = request.GET.get('query', '')
    if query:
        users = User.objects.filter(Q(username__istartswith=query) | Q(name__istartswith=query))        
        user_serializer = UserModelSerializer(users, many=True)        
        return Response(user_serializer.data)
    else:
        return Response([], status=204)

@ratelimit(key='ip', rate='25/m', block=True)
@api_view(['GET'])
@permission_classes([AllowAny])
def checkUsername(request):
    username = request.GET.get('username', None)
    if username:
        lowercase = username.lower()
        is_taken = User.objects.filter(username__iexact=lowercase).exists()
        if is_taken:
            return Response({"message": "Username is already taken", "is_taken": True}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Username is available", "is_taken": False}, status=status.HTTP_200_OK)
    return Response("Invalid username", status=status.HTTP_400_BAD_REQUEST)

# TODO: Reserach defenses against injection attacks
@ratelimit(key='ip', rate='5/m', block=True)
@api_view(['POST'])
@permission_classes([AllowAny])
def createUser(request):
    serializer = UserModelSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()  # Save the validated object
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@ratelimit(key='ip', rate='5/m', block=True)
@api_view(['PUT'])
@authentication_classes([SupabaseAuthentication])
@permission_classes([IsAuthenticated])
def updateUser(request, username):
    data = request.data
    user = User.objects.get(username=username)
    serializer = UserModelSerializer(user, data=request.data, partial=True)  # Allow partial updates
    if serializer.is_valid():
        # Only update the fields that are present in the request data
        if 'username' in data:
            user.username = data['username']
        # if 'password' in data:
        #     user.password = data['password']
        if 'name' in data:
            user.name = data['name']
        if 'email' in data:
            user.email = data['email']
        if 'bio' in data:
            user.bio = data['bio']
        if 'user_type' in data:
            user.user_type = data['user_type']
        if 'user_privacy' in data:
            user.user_privacy = data['user_privacy']
        
        # Save the user object to update the fields
        user.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@ratelimit(key='ip', rate='20/m', block=True)
@api_view(['POST'])
@authentication_classes([SupabaseAuthentication])
@permission_classes([IsAuthenticated])
def followUser(request, your_username, user_username):
    try:
        # Following other user
        yourself = User.objects.get(username=your_username)
        # User being followed
        user = User.objects.get(username=user_username)

        if yourself in user.follow_requests.all():
            user.follow_requests.remove(yourself)
            yourself.requesting_users.remove(user)

        yourself.list_of_following.add(user)
        user.list_of_followers.add(yourself)
        Notification.objects.create(sender=yourself, recipient=user, notification_type='follower')

        if user.expo_push_token:
            send_push_notifications(user.expo_push_token, 'New Follower', f'{yourself.username} followed you.')

        yourself.save()
        user.save()
        return Response('Successfully followed user', status=status.HTTP_201_CREATED)
    except:
        return Response('Too many requests. Try again later.', status=status.HTTP_429_TOO_MANY_REQUESTS)

@ratelimit(key='ip', rate='20/m', block=True)
@api_view(['POST'])
@authentication_classes([SupabaseAuthentication])
@permission_classes([IsAuthenticated])
def requestToFollowUser(request, your_username, user_username):
    try:
        # Requester
        yourself = User.objects.get(username=your_username)
        # Recipient of request
        user = User.objects.get(username=user_username)

        yourself.requesting_users.add(user)
        user.follow_requests.add(yourself)
        Notification.objects.create(sender=yourself, recipient=user, notification_type='request')
        if user.expo_push_token:
            send_push_notifications(user.expo_push_token, 
                                    'Follow Request', 
                                    f'{yourself.username} is requesting to follow you.')
        return Response('Sucessfully requested to follow user', status=status.HTTP_201_CREATED)
    except:
        return Response('Too many requests. Try again later.', status=status.HTTP_429_TOO_MANY_REQUESTS)

@ratelimit(key='ip', rate='20/m', block=True)
@api_view(['DELETE'])
@authentication_classes([SupabaseAuthentication])
@permission_classes([IsAuthenticated])
def removeRequestToFollowUser(request, your_username, user_username):
    try:
        yourself = User.objects.get(username=your_username)
        user = User.objects.get(username=user_username)

        yourself.requesting_users.remove(user)
        user.follow_requests.remove(yourself)
        return Response('Successfully removed request to follow user')
    except:
        return Response('Too many requests. Try again later.', status=status.HTTP_429_TOO_MANY_REQUESTS)

@ratelimit(key='ip', rate='20/m', block=True)
@api_view(['DELETE'])
@authentication_classes([SupabaseAuthentication])
@permission_classes([IsAuthenticated])
def unfollowUser(request, your_username, user_username):
    try:
        yourself = User.objects.get(username=your_username)
        user = User.objects.get(username=user_username)

        yourself.list_of_following.remove(user)
        user.list_of_followers.remove(yourself)
        return Response('Successfully unfollowed user')
    except:
        return Response('Too many requests. Try again later.', status=status.HTTP_429_TOO_MANY_REQUESTS)

@ratelimit(key='ip', rate='10/m', block=True)
@api_view(['POST'])
@authentication_classes([SupabaseAuthentication])
@permission_classes([IsAuthenticated])
def addUserNotification(request, your_username, user_username):
    try:
        yourself = User.objects.get(username=your_username)
        user = User.objects.get(username=user_username)

        if user not in yourself.subscriptions.all() and user in yourself.list_of_following.all() and yourself not in user.blocked_users.all():
            yourself.subscriptions.add(user)
        yourself.save()
        return Response('Successfully set notifications for user.')
    except:
        return Response('Too many requests. Try again later.', status=status.HTTP_429_TOO_MANY_REQUESTS)

@ratelimit(key='ip', rate='10/m', block=True)
@api_view(['DELETE'])
@authentication_classes([SupabaseAuthentication])
@permission_classes([IsAuthenticated])
def removeUserNotification(request, your_username, user_username):
    try:
        yourself = User.objects.get(username=your_username)
        user = User.objects.get(username=user_username)

        if user in yourself.subscriptions.all():
            yourself.subscriptions.remove(user)
        yourself.save()
        return Response('Successfully removed user notifications for this user.')
    except:
        return Response('Too many requests. Try again later.', status=status.HTTP_429_TOO_MANY_REQUESTS)

@ratelimit(key='ip', rate='10/m', block=True)
@api_view(['POST'])
@authentication_classes([SupabaseAuthentication])
@permission_classes([IsAuthenticated])
def blockUser(request, your_username, user_username):
    try:
        yourself = User.objects.get(username=your_username)
        user = User.objects.get(username=user_username)

        if user in yourself.list_of_followers.all():
            yourself.list_of_followers.remove(user)
            user.list_of_following.remove(yourself)
        
        if user in yourself.follow_requests.all():
            yourself.follow_requests.remove(user)
            user.requesting_users.remove(yourself)
        
        if user in yourself.subscriptions.all():
            yourself.subscriptions.remove(user)
        
        if yourself in user.list_of_followers.all():
            user.list_of_followers.remove(yourself)
            yourself.list_of_following.remove(user)

        if yourself in user.follow_requests.all():
            user.follow_requests.remove(yourself)
            yourself.requesting_users.remove(user)

        if yourself in user.subscriptions.all():
            user.subscriptions.remove(yourself)

        for event in yourself.created_events.all():
            if user in event.list_of_attendees.all():
                event.list_of_attendees.remove(user)
                user.attending_events.remove(event)
        
        yourself.blocked_users.add(user)
        yourself.save()
        user.save()
        return Response('Successfully blocked user', status=status.HTTP_201_CREATED)
    except:
        return Response('Too many requests. Try again later.', status=status.HTTP_429_TOO_MANY_REQUESTS)

@ratelimit(key='ip', rate='10/m', block=True)
@api_view(['DELETE'])
@authentication_classes([SupabaseAuthentication])
@permission_classes([IsAuthenticated])
def unblockUser(request, your_username, user_username):
    try:
        yourself = User.objects.get(username=your_username)
        user = User.objects.get(username=user_username)

        if user in yourself.blocked_users.all():
            yourself.blocked_users.remove(user)
        yourself.save()
        return Response('Successfully unblocked user')
    except:
        return Response('Too many requests. Try again later.', status=status.HTTP_429_TOO_MANY_REQUESTS)

@ratelimit(key='ip', rate='3/m', block=True)
@api_view(['DELETE'])
# @authentication_classes([SupabaseAuthentication])
# @permission_classes([IsAuthenticated])
def deleteUser(request, username):
    try:
        user = User.objects.get(username=username)
        user.delete()
        return Response('User successfully deleted')
    except:
        return Response('Too many requests. Try again later.', status=status.HTTP_429_TOO_MANY_REQUESTS)

# EVENT API ENDPOINTS
# For development, not used in app
@api_view(['GET'])
@permission_classes([AllowAny])
def getEvents(request):
    events = Event.objects.all()
    serializer = EventModelSerializer(events, many=True)
    return Response(serializer.data)

@ratelimit(key='ip', rate='50/m', block=True)
@api_view(['GET'])
@authentication_classes([SupabaseAuthentication])
@permission_classes([IsAuthenticated])
def getEvent(request, id):
    event = Event.objects.get(id=id)
    serializer = EventModelSerializer(event, many=False)
    return Response(serializer.data)

@ratelimit(key='ip', rate='30/m', block=True)
@api_view(['GET'])
@permission_classes([AllowAny])
def searchEvents(request):
    query = request.GET.get('query', '')
    if query:
        events = Event.objects.filter(Q(event_name__icontains=query)
                                    | Q(event_description__icontains=query) | Q(location_addr__icontains=query))
        event_serializer = EventModelSerializer(events, many=True)
        return Response(event_serializer.data)
    else:
        return Response([], status=200)

@ratelimit(key='ip', rate='20/m', block=True)
@api_view(['GET'])
@authentication_classes([SupabaseAuthentication])
@permission_classes([IsAuthenticated])
def getEventAttendees(request, id):
    event = Event.objects.get(id=id)
    attendees = event.list_of_attendees.all()
    serializer = UserModelSerializer(attendees, many=True)
    return Response(serializer.data)

@ratelimit(key='ip', rate='50/m', block=True)
@api_view(['GET'])
@authentication_classes([SupabaseAuthentication])
@permission_classes([IsAuthenticated])
def getEventsOfFollowing(request, username):
    # firebaseUser = request.user  # Now you have the authenticated user
    user = User.objects.get(username=username)
    followedUsers = user.list_of_following.all()
    events = Event.objects.filter(creation_user__in=followedUsers)
    serializer = EventModelSerializer(events, many=True)
    # Always return a consistent JSON structure
    return Response(serializer.data if events.exists() else [])
    # if len(events) == 0:
    #     return Response("There are no events present.")
    # else:
    #     return Response(serializer.data)

@ratelimit(key='ip', rate='50/m', block=True)
@api_view(['GET'])
@authentication_classes([SupabaseAuthentication])
@permission_classes([IsAuthenticated])
def getFriendsAttendingEvent(request, username):
    user = User.objects.get(username=username)
    followedUsers = user.list_of_following.all()
    events_that_friends_are_attending = Event.objects.filter(list_of_attendees__in=followedUsers).distinct()
    serializer = EventModelSerializer(events_that_friends_are_attending, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@authentication_classes([SupabaseAuthentication])
@permission_classes([IsAuthenticated])
def getNearbyEvents(request, latitude, longitude):
    lat = float(latitude)
    lon = float(longitude)
    user_location = Point(lon, lat, srid=4326)
    radius = 50000
    events = Event.objects.annotate(distance=Distance('location_point', user_location)).filter(distance__lte=radius).order_by('distance')[:10]
    serializer = EventModelSerializer(events, many=True)
    return Response(serializer.data)

@ratelimit(key='ip', rate='5/m', block=True)
@api_view(['POST'])
@authentication_classes([SupabaseAuthentication])
@permission_classes([IsAuthenticated])
def createEvent(request):
    data = request.data
    location_point_data = data.get('location_point', {})
    latitude = location_point_data.get('latitude')
    longitude = location_point_data.get('longitude')
    event_limit = 3
    
    if latitude and longitude:
        location_point = Point(float(longitude), float(latitude), srid=4326)
        data['location_point'] = location_point
    else:
        data['location_point'] = None
    
    serializer = EventModelSerializer(data=data)
    
    if serializer.is_valid():
        creation_user_id = data['creation_user']
        user = User.objects.get(id=creation_user_id)
        if user.created_events.count() >= event_limit:
            return Response("You can only create a maximum of 3 events", status=status.HTTP_400_BAD_REQUEST)

        # Create a new event using serializer
        event = serializer.save(creation_user=user)

        # Adds the event to the created_events field for the creation user
        user.created_events.add(event)
        user.save()

        # Refresh the serializer with the created event
        event_serializer = EventModelSerializer(event)
        return Response(event_serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@ratelimit(key='ip', rate='5/m', block=True)
@api_view(['PUT'])
@authentication_classes([SupabaseAuthentication])
@permission_classes([IsAuthenticated])
def updateEvent(request, id):
    data = request.data
    event = Event.objects.get(id=id)
    serializer = EventModelSerializer(event, data=request.data, partial=True)
    if serializer.is_valid():
        event.event_name = data['event_name']
        event.event_description = data['event_description']
        event.location_addr = data['location']
        event.date = data['date']
        
        if 'list_of_attendees' in data:
            list_of_attendees = data['list_of_attendees']
            event.list_of_attendees.set(list_of_attendees)
        event.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@ratelimit(key='ip', rate='20/m', block=True)
@api_view(['POST'])
@authentication_classes([SupabaseAuthentication])
@permission_classes([IsAuthenticated])
def registerUserForEvent(request, event_id, user_username):
    event = Event.objects.get(id=event_id)
    user = User.objects.get(username=user_username)

    event.list_of_attendees.add(user)
    user.attending_events.add(event)
    Notification.objects.create(sender=user, recipient=event.creation_user, notification_type='event_registration', event=event)
    if event.creation_user.expo_push_token:
        send_push_notifications(event.creation_user.expo_push_token, 
                                'Event Notification',
                                f'{user.username} is going your event: {event.event_name}')
    return Response('User successfully registered for the event', status=status.HTTP_201_CREATED)

@ratelimit(key='ip', rate='20/m', block=True)
@api_view(['DELETE'])
@authentication_classes([SupabaseAuthentication])
@permission_classes([IsAuthenticated])
def unregisterUserForEvent(request, event_id, user_username):
    event = Event.objects.get(id=event_id)
    user = User.objects.get(username=user_username)

    event.list_of_attendees.remove(user)
    user.attending_events.remove(event)
    return Response('User successfully unregistered for the event')

@ratelimit(key='ip', rate='10/m', block=True)
@api_view(['DELETE'])
@authentication_classes([SupabaseAuthentication])
@permission_classes([IsAuthenticated])
def deleteEvent(request, id):
    event = Event.objects.get(id=id)

    # Removes the event from the creation_user's created_events field
    user = event.creation_user
    user.created_events.remove(event)
    event.delete()
    return Response('Event successfully deleted')

@ratelimit(key='ip', rate='20/m', block=True)
@api_view(['GET'])
@authentication_classes([SupabaseAuthentication])
@permission_classes([IsAuthenticated])
def followerNotification(request, user_id):
    user = User.objects.get(id=user_id)
    follower_notifications = Notification.objects.filter(recipient=user, notification_type='follower').order_by('timestamp')[:10]

    if follower_notifications.exists():
        serializer = NotificationModelSerializer(follower_notifications, many=True)
        return Response(serializer.data)
    return Response('No new notifications', status=status.HTTP_204_NO_CONTENT)

@ratelimit(key='ip', rate='20/m', block=True)
@api_view(['GET'])
@authentication_classes([SupabaseAuthentication])
@permission_classes([IsAuthenticated])
def eventRegNotification(request, user_id):
    user = User.objects.get(id=user_id)
    event_notifications = Notification.objects.filter(recipient=user, notification_type='event_registration').order_by('timestamp')[:15]

    if event_notifications.exists():
        serializer = NotificationModelSerializer(event_notifications, many=True)
        return Response(serializer.data)
    return Response([], status=status.HTTP_204_NO_CONTENT)

@ratelimit(key='ip', rate='5/m', block=True)
@api_view(['POST'])
@authentication_classes([SupabaseAuthentication])
@permission_classes([IsAuthenticated])
def setImageURI(request, username):
    user = User.objects.get(username=username)
    uri = request.data.get('uri')
    if uri:
        user.profile_pic = uri
        user.save()
        return Response("Profile picture URI set.", status=status.HTTP_200_OK)
    return Response("No URI provided", status=status.HTTP_400_BAD_REQUEST)

@ratelimit(key='ip', rate='50/m', block=True)
@api_view(['POST'])
@authentication_classes([SupabaseAuthentication])
@permission_classes([IsAuthenticated])
def setExpoPushToken(request):
    username = request.data.get('username')
    pushToken = request.data.get('expo_push_token')

    user = User.objects.get(username=username)
    user.expo_push_token = pushToken
    user.save()
    return Response("Push token successfully saved.", status=status.HTTP_200_OK)

def send_push_notifications(expo_push_token, title, body):
    url = 'https://exp.host/--/api/v2/push/send'

    headers = {
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip, deflate',
        'Content-Type': 'application/json',
    }

    payload = {
        'to': expo_push_token,
        'sound': 'default',
        'title': title,
        'body': body,
        'data': {'extra_data': 'some value'}
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        return Response("Sent push notification", status=status.HTTP_200_OK)
    else:
        return Response("Failed to send request: ", status=status.HTTP_400_BAD_REQUEST)