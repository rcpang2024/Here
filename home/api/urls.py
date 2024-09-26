from . import views
from django.urls import path
from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView)

urlpatterns = [
    path('users/', views.getUsers, name="users"),
    path('users/id/<str:id>/', views.getUserByID, name="user-id"),
    path('users/username/<str:username>/', views.getUserByUsername, name="user-username"),
    path('users/email/<str:email>/', views.getUserByEmail, name="user-email"),
    path('createuser/', views.createUser, name="create-user"),
    path('updateuser/<str:username>/', views.updateUser, name="update-user"),
    path('followuser/<str:your_username>/<str:user_username>/', views.followUser, name="follow-user"),
    path('request_to_follow_user/<str:your_username>/<str:user_username>/', views.requestToFollowUser, name="request_to_follow-user"),
    path('unfollowuser/<str:your_username>/<str:user_username>/', views.unfollowUser, name="unfollow-user"),
    path('remove_request/<str:your_username>/<str:user_username>/', views.removeRequestToFollowUser, name="remove_request"),
    path('setnotification/<str:your_username>/<str:user_username>/', views.addUserNotification, name="set-notification"),
    path('removenotification/<str:your_username>/<str:user_username>/', views.removeUserNotification, name="remove-notification"),
    path('blockuser/<str:your_username>/<str:user_username>/', views.blockUser, name="block-user"),
    path('unblockuser/<str:your_username>/<str:user_username>/', views.unblockUser, name="unblock-user"),
    path('deleteuser/<str:username>/', views.deleteUser, name="delete-user"),
    path('events/', views.getEvents, name="events"),
    path('events/<str:id>/', views.getEvent, name="event"),
    path('createevent/', views.createEvent, name="create-event"),
    path('updateevent/<str:id>/', views.updateEvent, name="update-event"),
    path('registeruser/<str:event_id>/<str:user_username>/', views.registerUserForEvent, name="register-event"),
    path('unregisteruser/<str:event_id>/<str:user_username>/', views.unregisterUserForEvent, name="unregister-event"),
    path('deleteevent/<str:id>/', views.deleteEvent, name="delete-event"),
    path('searchusers/', views.searchUsers, name='search-users'),
    path('checkusername', views.checkUsername, name='check-username'),
    path('searchevents/', views.searchEvents, name='search-events'),
    path('friendsevents/<str:username>/', views.getEventsOfFollowing, name='friends-events'),
    path('friends_attending_events/<str:username>/', views.getFriendsAttendingEvent, name='friends-attending'),
    path('nearby_events/<str:latitude>/<str:longitude>/', views.getNearbyEvents, name="nearby-events"),
    path('follower_notifications/<str:user_id>/', views.followerNotification, name="follower-notification"),
    path('event_notifications/<str:user_id>/', views.eventRegNotification, name="event-notification"),
    path('set_picture/<str:username>/', views.setImageURI, name="set-profile-picture"),
    path('set_push_token/', views.setExpoPushToken, name="set-expo-token"),
    path('authenticate/', views.authenticate_user, name='authenticate-user'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh')
]