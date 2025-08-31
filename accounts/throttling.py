from rest_framework.throttling import SimpleRateThrottle
from django.core.cache import cache
import hashlib


class LoginRateThrottle(SimpleRateThrottle):
    """
    Throttle login attempts to 5 per minute per IP address.
    """
    scope = 'login'
    rate = '5/minute'

    def get_cache_key(self, request, view):
        # Use IP address as the cache key
        return f"login_throttle_{self.get_ident(request)}"

    def get_ident(self, request):
        """
        Identify the client by IP address.
        """
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        if xff:
            return xff.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')


class PasswordResetRateThrottle(SimpleRateThrottle):
    """
    Throttle password reset requests to 3 per hour per email address.
    """
    scope = 'password_reset'
    rate = '3/hour'

    def get_cache_key(self, request, view):
        # Use email address as the cache key
        email = request.data.get('email', '')
        if email:
            # Hash the email for security
            email_hash = hashlib.md5(email.encode()).hexdigest()
            return f"password_reset_throttle_{email_hash}"
        return None

    def allow_request(self, request, view):
        # If no email provided, don't throttle (will be caught by validation)
        if not request.data.get('email'):
            return True
        
        return super().allow_request(request, view)

    def throttle_failure(self):
        """
        Return a custom error message for password reset throttling.
        """
        return {
            'error': 'Too many password reset requests',
            'message': 'You have exceeded the limit of 3 password reset requests per hour. Please try again later.',
            'retry_after': self.wait()
        }
