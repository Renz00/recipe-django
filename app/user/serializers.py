"""
Serializes for the user API view.
"""
from django.contrib.auth import (
    get_user_model,
    authenticate
)
from django.utils.translation import gettext as _

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
        This overrides the default create method for User model.
        """
        # We set the create method to use the create_user method
        # from the user model manager.
        # We use this method to avoid the default behaviour when storing
        # new data in models because the password needs to be hashed
        # before storing it
        return get_user_model().objects.create_user(**validated_data)

    def update(self, user_instance, validated_data):
        """
        Override the default update method and return user.
        'instance' is the model instance that will be updated.
        """
        # If password exists, retrieve the password value from the
        # validated data dict then remove it from the dict.
        # Password default is None if there is no password found.
        password = validated_data.pop('password', None)
        # Call the parent class update method to update the user.
        # The password was popped out so it will not be included.
        # This is because we will need to hash the password before
        # saving it.
        user = super().update(user_instance, validated_data)

        # Check if a password was provided then hash the
        # new password and save the user.
        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """
    Serializer for the user authentication token.
    This is using the Serializer class so there is no Meta class needed.
    We don't user Model class because Token does not have a model and is
    just an additional functionality.
    """
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        # Prevents automatic trimming of whitespace
        trim_whitespace=False
    )

    def validate(self, attrs):
        """
        Validate and authenticate the user.
        """
        email = attrs.get('email')
        password = attrs.get('password')

        # Authenticate the user
        user = authenticate(
            # this contains the header contents of the request
            request=self.context.get('request'),
            # we set email as username because we have
            # customized the user model
            username=email,
            password=password
        )

        # If authentication fails, raise an error
        if not user:
            msg = _('Unable to authenticate with provided credentials')
            # This exception will return the error message to the client
            raise serializers.ValidationError(msg, code='authentication')

        # Set the user in the context
        attrs['user'] = user
        return attrs
