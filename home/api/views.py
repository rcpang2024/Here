from rest_framework import viewsets, generics, status
from rest_framework.views import APIView
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

# @api_view(['POST'])
# def createUser(request):
#     data = request.data
#     username = data['username']
#     # Check if user with the given username already exists
#     existing_user = User.objects.filter(username=username).exists()
#     if existing_user:
#         return Response({'error': 'User with this username already exists'}, status=status.HTTP_400_BAD_REQUEST)
#     # Create a new user
#     user = User.objects.create(
#         username=data['username'],
#         name=data['name'],
#         email=data['email'],
#         phone_number=data['phone_number'],
#         list_of_followers=data['list_of_followers'],
#         list_of_following=data['list_of_following'],
#         user_type=data['user_type'],
#         created_events=data['created_events'],
#         attending_events=data['attending_events']
#     )
#     serializer = UserModelSerializer(user, many=False)
#     return Response(serializer.data, status=status.HTTP_201_CREATED)

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

# class UserViewSet(viewsets.ModelViewSet):
#     queryset = User.objects.all()
#     serializer_class = UserModelSerializer

# class EventViewSet(viewsets.ModelViewSet):
#     queryset = Event.objects.all()
#     serializer_class = EventModelSerializer
