from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.core.cache import cache
import json

User = get_user_model()


class UserModelTest(TestCase):
    """Test cases for the custom User model."""
    
    def setUp(self):
        self.user_data = {
            'full_name': 'John Doe',
            'email': 'john@example.com',
            'password': 'testpass123'
        }
    
    def test_create_user(self):
        """Test creating a user with valid data."""
        user = User.objects.create_user(
            email=self.user_data['email'],
            full_name=self.user_data['full_name'],
            password=self.user_data['password']
        )
        
        self.assertEqual(user.email, self.user_data['email'])
        self.assertEqual(user.full_name, self.user_data['full_name'])
        self.assertTrue(user.check_password(self.user_data['password']))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
    
    def test_create_superuser(self):
        """Test creating a superuser."""
        superuser = User.objects.create_superuser(
            email='admin@example.com',
            full_name='Admin User',
            password='adminpass123'
        )
        
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
    
    def test_user_str_representation(self):
        """Test the string representation of the user."""
        user = User.objects.create_user(
            email=self.user_data['email'],
            full_name=self.user_data['full_name'],
            password=self.user_data['password']
        )
        
        self.assertEqual(str(user), self.user_data['email'])


class UserRegistrationTest(APITestCase):
    """Test cases for user registration endpoint."""
    
    def setUp(self):
        self.register_url = reverse('register')
        self.valid_data = {
            'full_name': 'Jane Doe',
            'email': 'jane@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        }
    
    def test_user_registration_with_valid_data(self):
        """Test successful user registration with valid data."""
        response = self.client.post(self.register_url, self.valid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertIn('user', response.data)
        self.assertIn('tokens', response.data)
        self.assertEqual(response.data['user']['email'], self.valid_data['email'])
        self.assertEqual(response.data['user']['full_name'], self.valid_data['full_name'])
        
        # Verify user was created in database
        user = User.objects.get(email=self.valid_data['email'])
        self.assertEqual(user.full_name, self.valid_data['full_name'])
    
    def test_user_registration_with_invalid_email(self):
        """Test user registration with invalid email format."""
        invalid_data = self.valid_data.copy()
        invalid_data['email'] = 'invalid-email'
        
        response = self.client.post(self.register_url, invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
    
    def test_user_registration_with_mismatched_passwords(self):
        """Test user registration with mismatched passwords."""
        invalid_data = self.valid_data.copy()
        invalid_data['password_confirm'] = 'differentpassword'
        
        response = self.client.post(self.register_url, invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
    
    def test_user_registration_with_duplicate_email(self):
        """Test user registration with existing email."""
        # Create a user first
        User.objects.create_user(
            email=self.valid_data['email'],
            full_name=self.valid_data['full_name'],
            password=self.valid_data['password']
        )
        
        # Try to register with same email
        response = self.client.post(self.register_url, self.valid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
    
    def test_user_registration_with_weak_password(self):
        """Test user registration with weak password."""
        invalid_data = self.valid_data.copy()
        invalid_data['password'] = '123'
        invalid_data['password_confirm'] = '123'
        
        response = self.client.post(self.register_url, invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)


class UserLoginTest(APITestCase):
    """Test cases for user login endpoint."""
    
    def setUp(self):
        self.login_url = reverse('login')
        self.user_data = {
            'full_name': 'Test User',
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        self.user = User.objects.create_user(
            email=self.user_data['email'],
            full_name=self.user_data['full_name'],
            password=self.user_data['password']
        )
    
    def test_user_login_with_valid_credentials(self):
        """Test successful login with valid credentials."""
        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        
        response = self.client.post(self.login_url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertIn('user', response.data)
        self.assertIn('tokens', response.data)
        self.assertEqual(response.data['user']['email'], self.user_data['email'])
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])
    
    def test_user_login_with_invalid_email(self):
        """Test login with non-existent email."""
        login_data = {
            'email': 'nonexistent@example.com',
            'password': self.user_data['password']
        }
        
        response = self.client.post(self.login_url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
    
    def test_user_login_with_invalid_password(self):
        """Test login with incorrect password."""
        login_data = {
            'email': self.user_data['email'],
            'password': 'wrongpassword'
        }
        
        response = self.client.post(self.login_url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
    
    def test_user_login_with_inactive_user(self):
        """Test login with inactive user account."""
        self.user.is_active = False
        self.user.save()
        
        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        
        response = self.client.post(self.login_url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)


class PasswordResetTest(APITestCase):
    """Test cases for password reset functionality."""
    
    def setUp(self):
        self.request_reset_url = reverse('password_reset_request')
        self.confirm_reset_url = reverse('password_reset_confirm')
        self.user_data = {
            'full_name': 'Reset User',
            'email': 'reset@example.com',
            'password': 'oldpass123'
        }
        self.user = User.objects.create_user(
            email=self.user_data['email'],
            full_name=self.user_data['full_name'],
            password=self.user_data['password']
        )
        # Clear cache before each test
        cache.clear()
    
    def test_password_reset_request_with_valid_email(self):
        """Test password reset request with valid email."""
        reset_data = {
            'email': self.user_data['email']
        }
        
        response = self.client.post(self.request_reset_url, reset_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertIn('token', response.data)
        self.assertIn('expires_in', response.data)
        self.assertEqual(response.data['expires_in'], '10 minutes')
        
        # Verify token is stored in cache
        token = response.data['token']
        cache_key = f"password_reset_{token}"
        user_id = cache.get(cache_key)
        self.assertEqual(user_id, self.user.id)
    
    def test_password_reset_request_with_invalid_email(self):
        """Test password reset request with invalid email format."""
        reset_data = {
            'email': 'invalid-email'
        }
        
        response = self.client.post(self.request_reset_url, reset_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
    
    def test_password_reset_request_with_nonexistent_email(self):
        """Test password reset request with non-existent email."""
        reset_data = {
            'email': 'nonexistent@example.com'
        }
        
        response = self.client.post(self.request_reset_url, reset_data, format='json')
        
        # Should return success to prevent email enumeration
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
    
    def test_password_reset_confirm_with_valid_token(self):
        """Test password reset confirmation with valid token."""
        # First request a reset token
        reset_data = {
            'email': self.user_data['email']
        }
        response = self.client.post(self.request_reset_url, reset_data, format='json')
        token = response.data['token']
        
        # Confirm password reset
        confirm_data = {
            'token': token,
            'new_password': 'newpass123',
            'new_password_confirm': 'newpass123'
        }
        
        response = self.client.post(self.confirm_reset_url, confirm_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        
        # Verify password was changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpass123'))
        
        # Verify token was deleted from cache
        cache_key = f"password_reset_{token}"
        self.assertIsNone(cache.get(cache_key))
    
    def test_password_reset_confirm_with_invalid_token(self):
        """Test password reset confirmation with invalid token."""
        confirm_data = {
            'token': 'invalid-token',
            'new_password': 'newpass123',
            'new_password_confirm': 'newpass123'
        }
        
        response = self.client.post(self.confirm_reset_url, confirm_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Invalid or expired token')
    
    def test_password_reset_confirm_with_mismatched_passwords(self):
        """Test password reset confirmation with mismatched passwords."""
        # First request a reset token
        reset_data = {
            'email': self.user_data['email']
        }
        response = self.client.post(self.request_reset_url, reset_data, format='json')
        token = response.data['token']
        
        # Confirm password reset with mismatched passwords
        confirm_data = {
            'token': token,
            'new_password': 'newpass123',
            'new_password_confirm': 'differentpass123'
        }
        
        response = self.client.post(self.confirm_reset_url, confirm_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
    
    def test_password_reset_token_expiry(self):
        """Test that password reset tokens expire after 10 minutes."""
        # First request a reset token
        reset_data = {
            'email': self.user_data['email']
        }
        response = self.client.post(self.request_reset_url, reset_data, format='json')
        token = response.data['token']
        
        # Simulate token expiry by manually deleting from cache
        cache_key = f"password_reset_{token}"
        cache.delete(cache_key)
        
        # Try to confirm password reset with expired token
        confirm_data = {
            'token': token,
            'new_password': 'newpass123',
            'new_password_confirm': 'newpass123'
        }
        
        response = self.client.post(self.confirm_reset_url, confirm_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Invalid or expired token')


class RateLimitingTest(APITestCase):
    """Test cases for rate limiting functionality."""
    
    def setUp(self):
        self.login_url = reverse('login')
        self.request_reset_url = reverse('password_reset_request')
        self.user_data = {
            'full_name': 'Rate Test User',
            'email': 'rate@example.com',
            'password': 'testpass123'
        }
        self.user = User.objects.create_user(
            email=self.user_data['email'],
            full_name=self.user_data['full_name'],
            password=self.user_data['password']
        )
        cache.clear()
    
    def test_login_rate_limiting(self):
        """Test that login attempts are rate limited."""
        login_data = {
            'email': self.user_data['email'],
            'password': 'wrongpassword'
        }
        
        # Make 6 login attempts (exceeding the 5/minute limit)
        for i in range(6):
            response = self.client.post(self.login_url, login_data, format='json')
            if i < 5:
                # First 5 attempts should fail due to wrong password
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            else:
                # 6th attempt should be rate limited
                self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
    
    def test_password_reset_rate_limiting(self):
        """Test that password reset requests are rate limited."""
        reset_data = {
            'email': self.user_data['email']
        }
        
        # Make 4 password reset requests (exceeding the 3/hour limit)
        for i in range(4):
            response = self.client.post(self.request_reset_url, reset_data, format='json')
            if i < 3:
                # First 3 requests should succeed
                self.assertEqual(response.status_code, status.HTTP_200_OK)
            else:
                # 4th request should be rate limited
                self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
                self.assertIn('error', response.data)
                self.assertEqual(response.data['error'], 'Too many password reset requests')
