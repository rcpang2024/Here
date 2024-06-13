from . import views
from django.urls import path

# python manage.py runserver 192.168.1.142:8000

urlpatterns = [
    path('users/', views.getUsers, name="users"),
    path('users/id/<str:id>/', views.getUserByID, name="user-id"),
    path('users/username/<str:username>/', views.getUserByUsername, name="user-username"),
    path('createuser/', views.createUser, name="create-user"),
    path('updateuser/<str:username>/', views.updateUser, name="update-user"),
    path('followuser/<str:your_username>/<str:user_username>/', views.followUser, name="follow-user"),
    path('unfollowuser/<str:your_username>/<str:user_username>/', views.unfollowUser, name="unfollow-user"),
    path('deleteuser/<str:username>/', views.deleteUser, name="delete-user"),
    path('events/', views.getEvents, name="events"),
    path('events/<str:id>/', views.getEvent, name="event"),
    path('createevent/', views.createEvent, name="create-event"),
    path('updateevent/<str:id>/', views.updateEvent, name="update-event"),
    path('registeruser/<str:event_id>/<str:user_username>/', views.registerUserForEvent, name="register-event"),
    path('unregisteruser/<str:event_id>/<str:user_username>/', views.unregisterUserForEvent, name="unregister-event"),
    path('deleteevent/<str:id>/', views.deleteEvent, name="delete-event"),
    path('searchusers', views.searchUsers, name='search-users'),
    path('searchevents', views.searchEvents, name='search-events')
]