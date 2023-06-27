from rest_framework import routers
from rest_framework.views import APIView
from . import views
from django.urls import path, include

# router = routers.DefaultRouter()
# router.register(r'users', views.UserViewSet)
# router.register(r'events', views.EventViewSet)

urlpatterns = [
    #path('', include(router.urls)),
    path('users/', views.getUsers, name="users"),
    path('users/<str:username>/', views.getUser, name='user'),
    path('users/createuser/', views.createUser, name='create-user'),
    path('events/', views.getEvents, name="events"),
    path('events/<str:id>', views.getEvent, name="event"),
]