"""Serializers for recipe API"""
from rest_framework import serializers

from core.models import (
    Recipe,
    Tag
)


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipe object"""

    class Meta:
        model = Recipe
        # Fields that are expected to be provided in the requests
        # and will be saved in the model provided. If not satisfied,
        # a http bad response will be returned.
        fields = ['id', 'title', 'time_minutes', 'price', 'link']
        read_only_fields = ['id']


class RecipeDetailSerializer(RecipeSerializer):
    """
    Serializer for recipe detail object
    We are basing this class with the RecipeSerializer class
    since they share the same fields.
    """

    class Meta(RecipeSerializer.Meta):
        # We just add the description field to the fields list
        fields = RecipeSerializer.Meta.fields + ['description']


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag objects"""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        # Should not modify ID
        read_only_fields = ['id']