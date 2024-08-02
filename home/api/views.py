from rest_framework import status
from ..models import User, Event
from .serializers import UserModelSerializer, EventModelSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance

# USER API ENDPOINTS
@api_view(['GET'])
def getUsers(request):
    users = User.objects.all()
    serializer = UserModelSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getUserByID(request, id):
    user = User.objects.get(id=id)
    serializer = UserModelSerializer(user, many=False)
    return Response(serializer.data)

@api_view(['GET'])
def getUserByUsername(request, username):
    user = User.objects.get(username=username)
    serializer = UserModelSerializer(user, many=False)
    return Response(serializer.data)

@api_view(['GET'])
def getUserByEmail(request, email):
    user = User.objects.get(email=email)
    serializer = UserModelSerializer(user, many=False)
    return Response(serializer.data)

@api_view(['GET'])
def searchUsers(request):
    query = request.GET.get('query', '')
    if query:
        users = User.objects.filter(Q(username__istartswith=query) | Q(name__istartswith=query))        
        user_serializer = UserModelSerializer(users, many=True)        
        return Response(user_serializer.data)
    else:
        return Response([], status=204)
    
@api_view(['GET'])
def searchEvents(request):
    query = request.GET.get('query', '')
    if query:
        events = Event.objects.filter(Q(event_name__icontains=query)
                                      | Q(event_description__icontains=query) | Q(location_addr__icontains=query))
        event_serializer = EventModelSerializer(events, many=True)
        return Response(event_serializer.data)
    else:
        return Response([], status=200)

@api_view(['POST'])
def createUser(request):
    serializer = UserModelSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()  # Save the validated object
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def updateUser(request, username):
    data = request.data
    user = User.objects.get(username=username)
    serializer = UserModelSerializer(user, data=request.data, partial=True)  # Allow partial updates
    if serializer.is_valid():
        # Only update the fields that are present in the request data
        if 'username' in data:
            user.username = data['username']
        if 'password' in data:
            user.password = data['password']
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

@api_view(['POST'])
def followUser(request, your_username, user_username):
    yourself = User.objects.get(username=your_username)
    user = User.objects.get(username=user_username)

    yourself.list_of_following.add(user)
    user.list_of_followers.add(yourself)
    return Response('Successfully followed user', status=status.HTTP_201_CREATED)

@api_view(['POST'])
def requestToFollowUser(request, your_username, user_username):
    yourself = User.objects.get(username=your_username)
    user = User.objects.get(username=user_username)

    yourself.requesting_users.add(user)
    user.follow_requests.add(yourself)
    return Response('Sucessfully requested to follow user', status=status.HTTP_201_CREATED)

@api_view(['DELETE'])
def unfollowUser(request, your_username, user_username):
    yourself = User.objects.get(username=your_username)
    user = User.objects.get(username=user_username)

    yourself.list_of_following.remove(user)
    user.list_of_followers.remove(yourself)
    return Response('Successfully unfollowed user')

@api_view(['DELETE'])
def removeRequestToFollowUser(request, your_username, user_username):
    yourself = User.objects.get(username=your_username)
    user = User.objects.get(username=user_username)

    yourself.requesting_users.remove(user)
    user.follow_requests.remove(yourself)
    return Response('Successfully removed request to follow user')

@api_view(['DELETE'])
def deleteUser(request, username):
    user = User.objects.get(username=username)
    user.delete()
    return Response('User successfully deleted')

# EVENT API ENDPOINTS
@api_view(['GET'])
def getEvents(request):
    events = Event.objects.all()
    serializer = EventModelSerializer(events, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getEvent(request, id):
    event = Event.objects.get(id=id)
    serializer = EventModelSerializer(event, many=False)
    return Response(serializer.data)

@api_view(['GET'])
def getEventsOfFollowing(request, username):
    user = User.objects.get(username=username)
    followedUsers = user.list_of_following.all()
    events = Event.objects.filter(creation_user__in=followedUsers)
    serializer = EventModelSerializer(events, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getFriendsAttendingEvent(request, username):
    user = User.objects.get(username=username)
    followedUsers = user.list_of_following.all()
    events_that_friends_are_attending = Event.objects.filter(list_of_attendees__in=followedUsers).distinct()
    serializer = EventModelSerializer(events_that_friends_are_attending, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getNearbyEvents(request, latitude, longitude):
    lat = float(latitude)
    lon = float(longitude)
    user_location = Point(lon, lat, srid=4326)
    radius = 50000
    events = Event.objects.annotate(distance=Distance('location_point', user_location)).filter(distance__lte=radius).order_by('distance')[:10]
    serializer = EventModelSerializer(events, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def createEvent(request):
    data = request.data
    location_point_data = data.get('location_point', {})
    latitude = location_point_data.get('latitude')
    longitude = location_point_data.get('longitude')
    
    if latitude and longitude:
        location_point = Point(float(longitude), float(latitude), srid=4326)
        data['location_point'] = location_point
    else:
        data['location_point'] = None
    
    serializer = EventModelSerializer(data=data)
    
    if serializer.is_valid():
        creation_user_id = data['creation_user']
        user = User.objects.get(id=creation_user_id)

        # Create a new event using serializer
        event = serializer.save(creation_user=user)

        # Adds the event to the created_events field for the creation user
        user.created_events.add(event)
        user.save()

        # Refresh the serializer with the created event
        event_serializer = EventModelSerializer(event)
        return Response(event_serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
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

@api_view(['POST'])
def registerUserForEvent(request, event_id, user_username):
    event = Event.objects.get(id=event_id)
    user = User.objects.get(username=user_username)

    event.list_of_attendees.add(user)
    user.attending_events.add(event)
    return Response('User successfully registered for the event', status=status.HTTP_201_CREATED)

@api_view(['DELETE'])
def unregisterUserForEvent(request, event_id, user_username):
    event = Event.objects.get(id=event_id)
    user = User.objects.get(username=user_username)

    event.list_of_attendees.remove(user)
    user.attending_events.remove(event)
    return Response('User successfully unregistered for the event')

@api_view(['DELETE'])
def deleteEvent(request, id):
    event = Event.objects.get(id=id)

    # removes the event from the creation_user's created_events field
    user = event.creation_user
    user.created_events.remove(event)
    event.delete()
    return Response('Event successfully deleted')

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def friends_events(request):
#     user = request.user
#     following_ids = user.list_of_following.values_list('id', flat=True)
#     events = Event.objects.filter(creation_user__id__in=following_ids)
#     serializer = EventModelSerializer(events, many=True)
#     return Response(serializer.data)