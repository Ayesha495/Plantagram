from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model
    Used for displaying user information
    """
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'profile_picture', 
            'location', 'language_preference', 'streak_count', 
            'total_petal_points', 'league', 'created_at'
        ]
        read_only_fields = ['id', 'streak_count', 'total_petal_points', 'league', 'created_at']


class SignupSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration/signup
    Validates password and creates new user
    """
    password = serializers.CharField(
        write_only=True,  # Password won't be returned in response
        required=True,
        validators=[validate_password],  # Use Django's password validation
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True, 
        required=True,
        style={'input_type': 'password'},
        label='Confirm Password'
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'location', 'language_preference']
    
    def validate(self, attrs):
        """
        Check that the two password fields match
        """
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                "password": "Password fields didn't match."
            })
        return attrs
    
    def create(self, validated_data):
        """
        Create and return a new user with encrypted password
        """
        # Remove password2 as it's not part of the User model
        validated_data.pop('password2')
        
        # Create user with encrypted password
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            location=validated_data.get('location', ''),
            language_preference=validated_data.get('language_preference', 'en')
        )
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login
    Validates email and password
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )