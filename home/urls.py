from django.urls import path
from . import views

# URL Configuration
urlpatterns = [
    path('', views.get_users)
]