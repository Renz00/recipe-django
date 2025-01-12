"""Views for the Recipe API
"""
from rest_framework import (
    viewsets,
    mixins,
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import (
    Recipe,
    Tag,
    Ingredient
)
from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
    TagSerializer,
    IngredientSerializer
)


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Manage recipes in the database viewsets.

    ModelViewSet is used for CRUD endpoints
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
    # Adds support for token authentication
    authentication_classes = [TokenAuthentication]
    # User must be authenticated to perform any action
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


# The mixin classes should be provided before the viewset class
class TagViewSet(
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet):
    """
    Manage tags in the database viewsets.
    The GenericViewSet class inherits from GenericAPIView,
    and provides the default set of get_object, get_queryset
    methods and other generic view base behavior, but does not
    include any actions by default.

    In order to use a GenericViewSet class you'll override the class
    and either mixin the required mixin classes, or define the action
    implementations explicitly.

    The List Model Mixin provides a .list() method that implements
    listing a queryset. If the queryset is populated, this returns a 200 OK response,
    with a serialized representation of the queryset as the body of the
    response. The response data may optionally be paginated.
    """
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    # Enforce authentication and permission
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return objects for the current authenticated user only.
        This overrides the default get queryset behaviour for further
        customization.
        """
        return self.queryset\
            .filter(user=self.request.user)\
            .order_by('-name')


class IngredientViewSet(
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet):
    """
    Manage ingredients in the database viewsets.
    """
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    # Enforce authentication and permission
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return objects for the current authenticated user only.
        """
        return self.queryset\
            .filter(user=self.request.user)\
            .order_by('-name')