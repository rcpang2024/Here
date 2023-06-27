from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import User, Event
# from ..home.api.serializers import UserModelSerializer, EventModelSerializer

@api_view(['GET'])
def get_users(request):
    return Response("Placeholder")

# @api_view(['GET'])
# def get_user(request):
#     return Response("Placeholder")