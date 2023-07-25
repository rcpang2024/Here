from . import views
from django.urls import path, include

# python manage.py runserver 192.168.1.142:8000


urlpatterns = [
    path('users/', views.getUsers, name="users"),
    path('users/<str:id>/', views.getUser, name="user"),
    path('createuser/', views.createUser, name="create-user"),
    path('updateuser/<str:id>/', views.updateUser, name="update-user"),
    path('deleteuser/<str:username>/', views.deleteUser, name="delete-user"),
    path('events/', views.getEvents, name="events"),
    path('events/<str:id>/', views.getEvent, name="event"),
    path('createevent/', views.createEvent, name="create-event"),
    path('updateevent/<str:id>/', views.updateEvent, name="update-event"),
    path('deleteevent/<str:id>/', views.deleteEvent, name="delete-event"),
]