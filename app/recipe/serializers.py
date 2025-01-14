"""Serializers for recipe API"""
from rest_framework import serializers

from core.models import (
    Recipe,
    Tag,
    Ingredient,
)


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag objects"""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        # Should not modify ID
        read_only_fields = ['id']


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredient objects"""

    class Meta:
        model = Ingredient
        fields = ['id', 'name']
        # Should not modify ID
        read_only_fields = ['id']


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipe object"""
    # We are nesting the TagSerializer class here to associate
    # tags with recipes. We are also setting the required field to False
    tags = TagSerializer(many=True, required=False)
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        # Fields that will be validated in the requests
        # and will be saved in the model provided. If not satisfied,
        # a http bad response will be returned.
        fields = ['id', 'title', 'time_minutes', 'price',
                  'link', 'tags', 'ingredients', 'image']
        read_only_fields = ['id']

    # This helper function will be used in getting or creating recipes
    # and handling associated tags.
    def _get_or_create_tags(self, tags, recipe):
        """
        Get or create tags for the recipe as needed.
        """
        # Add the tags to the recipe using the many-to-many
        # relationship that was defined in the model.
        auth_user = self.context['request'].user
        for tag in tags:
            # Gets existing tag or creates a new one.
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            recipe.tags.add(tag_obj)
        # No need to return values here because these
        # functions will modify the recipe object directly.

    def _get_or_create_ingredients(self, ingredients, recipe):
        """
        Get or create ingredients for the recipe as needed.
        """
        # Add the ingredients to the recipe using the many-to-many
        # relationship that was defined in the model.
        auth_user = self.context['request'].user
        for ingredient in ingredients:
            # Gets existing ingredient or creates a new one.
            ingredient_obj, created = Ingredient.objects.get_or_create(
                user=auth_user,
                **ingredient,
            )
            recipe.ingredients.add(ingredient_obj)
        # No need to return values here because these
        # functions will modify the recipe object directly.

    def create(self, validated_data):
        """
        Create a new recipe.
        Since nested serializer are read only by default,
        We are overriding the create method to handle the tags.
        """
        # If the tags exist in the validated data, we pop it out
        # and store it in a separate variable. If it does not exist,
        # we default to an empty list.
        tags = validated_data.pop('tags', [])
        ingredients = validated_data.pop('ingredients', [])
        # Create the recipe. The tags are not included.
        recipe = Recipe.objects.create(**validated_data)

        self._get_or_create_tags(tags, recipe)
        self._get_or_create_ingredients(ingredients, recipe)

        return recipe

    def update(self, recipe_instance, validated_data):
        """
        Update a recipe.
        Since nested serializer are read only by default,
        We are overriding the update method to handle the tags.
        """
        # If the tags exist in the validated data, we pop it out
        # and store it in a separate variable. If it does not exist,
        # we default to an empty list.
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients', None)
        if tags is not None:
            # We clear all tags prior to updating the recipe.
            recipe_instance.tags.clear()
            # Then we call the helper function to get the existing tags
            # or create new ones.
            self._get_or_create_tags(tags, recipe_instance)
        if ingredients is not None:
            recipe_instance.ingredients.clear()
            self._get_or_create_ingredients(ingredients, recipe_instance)

        # We update the recipe model instance with the
        # validated data values.
        # The tags will not be included in this update because they were
        # already popped.
        for attr, value in validated_data.items():
            setattr(recipe_instance, attr, value)

        recipe_instance.save()
        return recipe_instance



class RecipeDetailSerializer(RecipeSerializer):
    """
    Serializer for recipe detail object
    We are basing this class with the RecipeSerializer class
    since they share the same fields.
    """

    class Meta(RecipeSerializer.Meta):
        # We just add the description field to the fields list
        fields = RecipeSerializer.Meta.fields + ['description']


class RecipeImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to recipes"""

    class Meta:
        model = Recipe
        fields = ['id', 'image']
        # Should not modify ID
        read_only_fields = ['id']
        # For validation
        extra_kwargs = {
            'image': {
                'required': 'True'
            }
        }