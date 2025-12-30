from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import SignupSerializer, LoginSerializer, UserSerializer

@api_view(['POST'])
@permission_classes([AllowAny])  # Anyone can signup
def signup_view(request):
    """
    API endpoint for user registration
    POST /api/auth/signup
    
    Body: {
        "username": "john_doe",
        "email": "john@example.com",
        "password": "securepass123",
        "password2": "securepass123",
        "location": "New York, USA",  # optional
        "language_preference": "en"    # optional
    }
    """
    serializer = SignupSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        
        # Generate JWT tokens for the new user
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'User created successfully',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])  # Anyone can login
def login_view(request):
    """
    API endpoint for user login
    POST /api/auth/login
    
    Body: {
        "email": "john@example.com",
        "password": "securepass123"
    }
    """
    serializer = LoginSerializer(data=request.data)
    
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        # Authenticate user
        # Django's authenticate expects username, but we use email
        # So we need to get the user first
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.get(email=email)
            
            # Check password
            if not user.check_password(password):
                return Response({
                    'error': 'Invalid credentials'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': 'Login successful',
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Must be logged in
def profile_view(request):
    """
    API endpoint to get current user's profile
    GET /api/auth/profile
    
    Headers: {
        "Authorization": "Bearer <access_token>"
    }
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)