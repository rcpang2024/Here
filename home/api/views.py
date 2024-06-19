from rest_framework import status
from ..models import User, Event
from .serializers import UserModelSerializer, EventModelSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

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
                                      | Q(event_description__icontains=query) | Q(location__icontains=query))
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
    serializer = UserModelSerializer(user, data=request.data)
    if serializer.is_valid():
        user.username = data['username']
        user.password = data['password']
        user.name = data['name']
        user.email = data['email']
        user.bio = data['bio']
        user.user_type = data['user_type']
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

@api_view(['DELETE'])
def unfollowUser(request, your_username, user_username):
    yourself = User.objects.get(username=your_username)
    user = User.objects.get(username=user_username)

    yourself.list_of_following.remove(user)
    user.list_of_followers.remove(yourself)
    return Response('Successfully unfollowed user')

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

@api_view(['POST'])
def createEvent(request):
    data = request.data
    serializer = EventModelSerializer(data=request.data)

    if serializer.is_valid():
        creation_user_id = data['creation_user']
        user = User.objects.get(id=creation_user_id)
        # Create a new event
        event = Event.objects.create(
            creation_user=user,
            event_name=data['event_name'],
            event_description=data['event_description'],
            location=data['location'],
            date=data['date'],
        )
        attendees=data['list_of_attendees']
        event.list_of_attendees.set(attendees)

        # Adds the event to the created_events field for the creation user
        user.created_events.add(event)
        user.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def updateEvent(request, id):
    data = request.data
    event = Event.objects.get(id=id)
    serializer = EventModelSerializer(event, data=request.data)
    if serializer.is_valid():
        creation_user_id = int(data['creation_user'])
        user = User.objects.get(id=creation_user_id)
        event.creation_user = user
        event.event_name = data['event_name']
        event.event_description = data['event_description']
        event.location = data['location']
        event.date = data['date']
        
        event.save()

        list_of_attendees = data['list_of_attendees']
        event.list_of_attendees.set(list_of_attendees)
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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def friends_events(request):
    user = request.user
    following_ids = user.list_of_following.values_list('id', flat=True)
    events = Event.objects.filter(creation_user__id__in=following_ids)
    serializer = EventModelSerializer(events, many=True)
    return Response(serializer.data)