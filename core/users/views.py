from django.shortcuts import render

from rest_framework import generics
from .models import User
from .serializers import RegisterSerializer

# view pentru inregistrare utilizator
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer