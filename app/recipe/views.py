"""Views for the Recipe API
"""
from rest_framework import (
    viewsets,
    mixins,
    status,
)
from rest_framework.decorators import action
from rest_framework.response import Response
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
    RecipeImageSerializer,
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
        # when the .list() action is called.
        # RecipeDetailsSerializer has all fields,
        # while RecipeSerializer has limited fields.
        if self.action == 'list':
            return RecipeSerializer
        elif self.action == 'upload_image':
            # This makes the upload_image action use the RecipeImageSerializer
            # This is a custom action that is added to the viewset.
            return RecipeImageSerializer

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

    # Creating a custom action.
    # detail=True means that the detail endpoint will be used for this action and
    # will need a url with the primary key (id) of the object.
    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to recipe"""
        # Gets the recipe object using the primary key
        recipe = self.get_object()
        # Serializes the data. This will use the RecipeImageSerializer
        # as specified in the get_serializer_class method.
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        # Will return all errors included in the serializer
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# The mixin classes should be provided before the viewset class
class BaseRecipeViewSet(
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet):
    """ Base viewset for user owned recipe attributes
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

    # Enforce authentication and permission
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self, order_by):
        """
        Return objects for the current authenticated user only.
        This overrides the default get queryset behaviour for further
        customization.
        """
        return self.queryset\
            .filter(user=self.request.user)\
            .order_by(order_by)


class TagViewSet(BaseRecipeViewSet):
    """
    Manage tags in the database viewsets.
    """
    serializer_class = TagSerializer
    queryset = Tag.objects.all()

    def get_queryset(self):
        return super().get_queryset('-name')


class IngredientViewSet(BaseRecipeViewSet):
    """
    Manage ingredients in the database viewsets.
    """
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()

    def get_queryset(self):
        return super().get_queryset('-id')