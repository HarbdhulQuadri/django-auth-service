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
    This endpoint allows users to create an account with email, full name, and password.
    
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
                            description: User's full name (required)
                            example: "John Doe"
                        email:
                            type: string
                            format: email
                            description: User's email address (used as username, must be unique)
                            example: "john@example.com"
                        password:
                            type: string
                            description: User's password (minimum 8 characters)
                            example: "securepass123"
                        password_confirm:
                            type: string
                            description: Password confirmation (must match password)
                            example: "securepass123"
    responses:
        201:
            description: User registered successfully
            content:
                application/json:
                    schema:
                        type: object
                        properties:
                            message:
                                type: string
                                example: "User registered successfully"
                            user:
                                type: object
                                properties:
                                    id:
                                        type: integer
                                        example: 1
                                    full_name:
                                        type: string
                                        example: "John Doe"
                                    email:
                                        type: string
                                        example: "john@example.com"
                            tokens:
                                type: object
                                properties:
                                    access:
                                        type: string
                                        description: JWT access token
                                        example: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
                                    refresh:
                                        type: string
                                        description: JWT refresh token
                                        example: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
        400:
            description: Invalid data provided
            content:
                application/json:
                    schema:
                        type: object
                        properties:
                            email:
                                type: array
                                items:
                                    type: string
                                example: ["This field must be unique."]
                            password:
                                type: array
                                items:
                                    type: string
                                example: ["This password is too short."]
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
                            example: "john@example.com"
                        password:
                            type: string
                            description: User's password
                            example: "securepass123"
    responses:
        200:
            description: Login successful
            content:
                application/json:
                    schema:
                        type: object
                        properties:
                            message:
                                type: string
                                example: "Login successful"
                            user:
                                type: object
                                properties:
                                    id:
                                        type: integer
                                        example: 1
                                    full_name:
                                        type: string
                                        example: "John Doe"
                                    email:
                                        type: string
                                        example: "john@example.com"
                            tokens:
                                type: object
                                properties:
                                    access:
                                        type: string
                                        description: JWT access token
                                        example: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
                                    refresh:
                                        type: string
                                        description: JWT refresh token
                                        example: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
        400:
            description: Invalid credentials
            content:
                application/json:
                    schema:
                        type: object
                        properties:
                            non_field_errors:
                                type: array
                                items:
                                    type: string
                                example: ["Unable to log in with provided credentials."]
        429:
            description: Too many login attempts
            content:
                application/json:
                    schema:
                        type: object
                        properties:
                            detail:
                                type: string
                                example: "Request was throttled. Expected available in 60 seconds."
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
                            example: "john@example.com"
    responses:
        200:
            description: Password reset token generated
            content:
                application/json:
                    schema:
                        type: object
                        properties:
                            message:
                                type: string
                                example: "Password reset token generated successfully"
                            token:
                                type: string
                                description: 32-character secure reset token
                                example: "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
                            expires_in:
                                type: string
                                description: Token expiry time
                                example: "10 minutes"
        400:
            description: Invalid email format
            content:
                application/json:
                    schema:
                        type: object
                        properties:
                            email:
                                type: array
                                items:
                                    type: string
                                example: ["Enter a valid email address."]
        429:
            description: Too many password reset requests
            content:
                application/json:
                    schema:
                        type: object
                        properties:
                            error:
                                type: string
                                example: "Too many password reset requests"
                            message:
                                type: string
                                example: "You have exceeded the limit of 3 password reset requests per hour. Please try again later."
                            retry_after:
                                type: integer
                                example: 3600
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
    Token must be valid and not expired (10-minute expiry).
    
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
                            description: Password reset token (32 characters)
                            example: "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
                        new_password:
                            type: string
                            description: New password (minimum 8 characters)
                            example: "newsecurepass123"
                        new_password_confirm:
                            type: string
                            description: New password confirmation (must match new_password)
                            example: "newsecurepass123"
    responses:
        200:
            description: Password reset successful
            content:
                application/json:
                    schema:
                        type: object
                        properties:
                            message:
                                type: string
                                example: "Password reset successful"
        400:
            description: Invalid token or passwords don't match
            content:
                application/json:
                    schema:
                        type: object
                        properties:
                            error:
                                type: string
                                example: "Invalid or expired token"
                            new_password:
                                type: array
                                items:
                                    type: string
                                example: ["This password is too short."]
                            new_password_confirm:
                                type: array
                                items:
                                    type: string
                                example: ["Passwords don't match."]
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
