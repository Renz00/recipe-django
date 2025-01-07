"""Views for the Recipe API
"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe
from recipe.serializers import (
    RecipeSerializer,
)


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Manage recipes in the database
    viewsets.ModelViewSet is used for CRUD endpoints
    to represent a single model instance.
    The actions provided by the ModelViewSet class are
    .list(), .retrieve(), .create(), .update(), .partial_update(),
    and .destroy()
    """
    serializer_class = RecipeSerializer
    # Specify the queryset to be used for managing the model
    queryset = Recipe.objects.all()
    # This is to verify the user is authenticated and
    # retrieve their identity.
    authentication_classes = [TokenAuthentication]
    # This is to verify the level of access of the user.
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return objects for the current authenticated user only
        """
        return self.queryset\
            .filter(user=self.request.user)\
            .order_by('-id')
