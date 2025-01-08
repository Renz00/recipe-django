"""Views for the Recipe API
"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe
from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer
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
    serializer_class = RecipeDetailSerializer
    # Specify the queryset to be used for managing the model
    queryset = Recipe.objects.all()
    # This is to verify the user is authenticated and
    # retrieve their identity.
    authentication_classes = [TokenAuthentication]
    # This is to verify the level of access of the user.
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return objects for the current authenticated user only.
        This overrides the default queryset behaviour for further
        customization.
        """
        return self.queryset\
            .filter(user=self.request.user)\
            .order_by('-id')

    def get_serializer_class(self):
        """
        Return appropriate serializer class.
        This overrides the default serializer class behaviour
        for further customization.
        """
        # We add this condition to limit the fields returned
        # RecipeDetailsSerializer has all fields
        # while RecipeSerializer has limited fields.
        if self.action == 'list':
            return RecipeSerializer

        # by default, return the provided serializer_class
        return self.serializer_class

    def perform_create(self, serializer):
        """
        Create a new recipe.
        This overrides the default create method for Recipe model.
        Param 'serializer' is the serialized and validated data
        that will be saved.
        """

        # We can access the currently authenticated user
        # using self.request.user
        serializer.save(user=self.request.user)
