from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import Throttled


def custom_exception_handler(exc, context):
    """
    Custom exception handler to provide better error messages for rate limiting.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    # Handle rate limiting exceptions
    if isinstance(exc, Throttled):
        # Get the throttle class to determine the type of throttling
        throttle_class = getattr(exc, 'throttle_class', None)
        
        if throttle_class and hasattr(throttle_class, 'scope'):
            if throttle_class.scope == 'login':
                response.data = {
                    'error': 'Too many login attempts',
                    'message': 'You have exceeded the limit of 5 login attempts per minute. Please try again later.',
                    'retry_after': exc.wait
                }
            elif throttle_class.scope == 'password_reset':
                response.data = {
                    'error': 'Too many password reset requests',
                    'message': 'You have exceeded the limit of 3 password reset requests per hour. Please try again later.',
                    'retry_after': exc.wait
                }
            else:
                response.data = {
                    'error': 'Rate limit exceeded',
                    'message': 'You have exceeded the rate limit. Please try again later.',
                    'retry_after': exc.wait
                }
        
        response.status_code = status.HTTP_429_TOO_MANY_REQUESTS
    
    return response
