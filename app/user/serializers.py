"""
Serializes for the user API view.
"""
from django.contrib.auth import get_user_model

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the user object.
    """

    class Meta:
        # State which model should be serialized.
        # We use get_user_model() to get the user model
        # that is used in the project.
        model = get_user_model()
        # Fields that are expected to be provided in the requests
        # and will be saved in the model provided. If not satisfied,
        # a http bad response will be returned.
        fields = ['email', 'password', 'name']
        # Extra keyword arguments to define the behavior of the fields
        # write_only means that the field will be used for input only and
        # will not be included in the returned response.
        # The min_length keyword argument will raise a validation error
        # and return an http bad response if not satisfied.
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validated_data):
        """
        Create a new user with encrypted password and return it.
        """
        # Use the create_user method from the user model manager.
        # We use this method to avoid the default behaviour when storing
        # new data in models because the password needs to be hashed
        # before storing it
        return get_user_model().objects.create_user(**validated_data)
