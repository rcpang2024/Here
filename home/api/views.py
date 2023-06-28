from rest_framework import status
from ..models import User, Event
from .serializers import UserModelSerializer, EventModelSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response

# USER API ENDPOINTS
@api_view(['GET'])
def getUsers(request):
    users = User.objects.all()
    serializer = UserModelSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getUser(request, username):
    user = User.objects.get(username=username)
    serializer = UserModelSerializer(user, many=False)
    return Response(serializer.data)

@api_view(['POST'])
def createUser(request):
    data = request.data
    username = data['username']
    # Check if user with the given username already exists
    existing_user = User.objects.filter(username=username).exists()
    if existing_user:
        return Response({'error': 'User with this username already exists'}, status=status.HTTP_400_BAD_REQUEST)
    # Create a new user
    
    serializer = UserModelSerializer(data=request.data)
    if serializer.is_valid():
        user = User.objects.create(
        username=data['username'],
        name=data['name'],
        email=data['email'],
        phone_number=data['phone_number'],
        user_type=data['user_type'],
        )
        followers=data['list_of_followers']
        following=data['list_of_following']
        created=data['created_events']
        attending=data['attending_events']
        user.list_of_followers.set(followers)
        user.list_of_following.set(following)
        user.created_events.set(created)
        user.attending_events.set(attending)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def updateUser(request, id):
    data = request.data
    user = User.objects.get(id=id)
    serializer = UserModelSerializer(user, data=request.data)
    if serializer.is_valid():
        user.username = data['username']
        user.name = data['name']
        user.email = data['email']
        user.phone_number = data['phone_number']
        user.user_type = data['user_type']
        
        # Save the user object to update the fields
        user.save()
        
        followers = data['list_of_followers']
        following = data['list_of_following']
        created = data['created_events']
        attending = data['attending_events']
        
        # Update the many-to-many relationships
        user.list_of_followers.set(followers)
        user.list_of_following.set(following)
        user.created_events.set(created)
        user.attending_events.set(attending)
        
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
    id = data['id']
    # Check if event with the given username already exists
    existing_event = Event.objects.filter(id=id).exists()
    if existing_event:
        return Response({'error': 'Event with this id already exists'}, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = EventModelSerializer(data=request.data)
    if serializer.is_valid():
        creation_user_id = int(data['creation_user'])
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

@api_view(['DELETE'])
def deleteEvent(request, id):
    event = Event.objects.get(id=id)
    event.delete()
    return Response('Event successfully deleted')