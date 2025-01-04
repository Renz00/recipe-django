"""Views for the user API
"""
from rest_framework import generics

from user.serializers import UserSerializer


class CreateUserView(generics.CreateAPIView):
    """
    Create a new user in the system
    """
    # The serializer will handle most of
    # the logic for creating new objects
    serializer_class = UserSerializer