"""URL mappings for the recipe app."""
from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from recipe import views


router = DefaultRouter()
# this will create a set of generic API endpoints for recipes/
# for each HTTP method
router.register('recipes', views.RecipeViewSet)
# Register the tags endpoint using router
router.register('tags', views.TagViewSet)
# Register the ingredients endpoint using router
router.register('ingredients', views.IngredientViewSet)

app_name = 'recipe'

urlpatterns = [
    path('', include(router.urls)),
]
