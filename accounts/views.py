from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.cache import cache
from django.contrib.auth import get_user_model
import secrets
import string
from .serializers import (
    UserRegistrationSerializer, 
    UserLoginSerializer, 
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer
)
from .throttling import LoginRateThrottle, PasswordResetRateThrottle

User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    Register a new user account.
    
    Creates a new user with the provided information and returns JWT tokens.
    
    ---
    requestBody:
        required: true
        content:
            application/json:
                schema:
                    type: object
                    required:
                        - full_name
                        - email
                        - password
                        - password_confirm
                    properties:
                        full_name:
                            type: string
                            description: User's full name
                        email:
                            type: string
                            format: email
                            description: User's email address (used as username)
                        password:
                            type: string
                            description: User's password
                        password_confirm:
                            type: string
                            description: Password confirmation
    responses:
        201:
            description: User registered successfully
        400:
            description: Invalid data provided
    """
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'User registered successfully',
            'user': {
                'id': user.id,
                'full_name': user.full_name,
                'email': user.email
            },
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            }
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([LoginRateThrottle])
def login_user(request):
    """
    Authenticate user and return JWT tokens.
    
    Validates user credentials and returns access and refresh tokens.
    Rate limited to 5 attempts per minute per IP address.
    
    ---
    requestBody:
        required: true
        content:
            application/json:
                schema:
                    type: object
                    required:
                        - email
                        - password
                    properties:
                        email:
                            type: string
                            format: email
                            description: User's email address
                        password:
                            type: string
                            description: User's password
    responses:
        200:
            description: Login successful
        400:
            description: Invalid credentials
        429:
            description: Too many login attempts
    """
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'full_name': user.full_name,
                'email': user.email
            },
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            }
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([PasswordResetRateThrottle])
def request_password_reset(request):
    """
    Request a password reset token.
    
    Generates a secure token and stores it in Redis with 10-minute expiry.
    Rate limited to 3 requests per hour per email address.
    
    ---
    requestBody:
        required: true
        content:
            application/json:
                schema:
                    type: object
                    required:
                        - email
                    properties:
                        email:
                            type: string
                            format: email
                            description: User's email address
    responses:
        200:
            description: Password reset token generated
        400:
            description: Invalid email format
        429:
            description: Too many password reset requests
    """
    serializer = PasswordResetRequestSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
            
            # Generate a secure token
            token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
            
            # Store token in Redis with 10 minutes expiry
            cache_key = f"password_reset_{token}"
            cache.set(cache_key, user.id, timeout=600)  # 10 minutes
            
            return Response({
                'message': 'Password reset token generated successfully',
                'token': token,
                'expires_in': '10 minutes'
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({
                'message': 'If the email exists, a password reset token has been generated'
            }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def confirm_password_reset(request):
    """
    Confirm password reset using token.
    
    Validates the reset token and updates the user's password.
    
    ---
    requestBody:
        required: true
        content:
            application/json:
                schema:
                    type: object
                    required:
                        - token
                        - new_password
                        - new_password_confirm
                    properties:
                        token:
                            type: string
                            description: Password reset token
                        new_password:
                            type: string
                            description: New password
                        new_password_confirm:
                            type: string
                            description: New password confirmation
    responses:
        200:
            description: Password reset successful
        400:
            description: Invalid token or passwords don't match
    """
    serializer = PasswordResetConfirmSerializer(data=request.data)
    if serializer.is_valid():
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']
        
        # Get user ID from Redis
        cache_key = f"password_reset_{token}"
        user_id = cache.get(cache_key)
        
        if user_id is None:
            return Response({
                'error': 'Invalid or expired token'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=user_id)
            user.set_password(new_password)
            user.save()
            
            # Delete the token from Redis
            cache.delete(cache_key)
            
            return Response({
                'message': 'Password reset successful'
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({
                'error': 'User not found'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
