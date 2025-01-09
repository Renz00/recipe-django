"""Views for the user API
"""
from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user.serializers import (
    UserSerializer,
    AuthTokenSerializer
)


class CreateUserView(generics.CreateAPIView):
    """
    Create a new user in the system.

    generics.CreateAPIView is used for create-only endpoints.
    This provides a POST method handler.
    """
    # The serializer will handle most of
    # the logic for creating new objects
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """
    Create a new auth token for user
    """
    serializer_class = AuthTokenSerializer
    # This is to enable a nice user interface for DRF (optional)
    rederer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """
    Manage the authenticated user.

    generics.RetrieveUpdateAPIView is used for read or update
    endpoints to represent a single model instance.
    Provides GET, PUT, PATCH methods handlers.
    """
    serializer_class = UserSerializer
    # This is to verify the user is authenticated and
    # retrieve their identity.
    authentication_classes = [TokenAuthentication]
    # This is to verify the level of access of the user.
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Retrieve and return authenticated user.
        This overrides the GET method response.
        """
        return self.request.user
