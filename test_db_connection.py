#!/usr/bin/env python3
"""
Simple script to test database and Redis connections.
Run this in Railway shell to debug connection issues.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auth_service.settings')
django.setup()

def test_environment_variables():
    """Test if all required environment variables are set."""
    print("🔍 Checking Environment Variables...")
    
    required_vars = ['SECRET_KEY', 'DEBUG', 'ALLOWED_HOSTS', 'DATABASE_URL', 'REDIS_URL']
    
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            if var in ['DATABASE_URL', 'REDIS_URL']:
                # Mask sensitive parts of connection strings
                if 'postgresql://' in value:
                    masked = value.replace(value.split('@')[0].split('://')[1], '***:***')
                elif 'redis://' in value:
                    masked = value.replace(value.split('@')[0].split('://')[1], '***:***')
                else:
                    masked = value
                print(f"✅ {var}: {masked}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: NOT SET")
    
    print()

def test_database_connection():
    """Test database connection."""
    print("🗄️ Testing Database Connection...")
    
    try:
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        print(f"✅ Database connection successful: {result}")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_redis_connection():
    """Test Redis connection."""
    print("🔴 Testing Redis Connection...")
    
    try:
        import redis
        from django.conf import settings
        
        # Get Redis URL from settings
        redis_url = getattr(settings, 'REDIS_URL', os.environ.get('REDIS_URL'))
        
        if not redis_url:
            print("❌ REDIS_URL not found in settings or environment")
            return False
        
        r = redis.from_url(redis_url)
        result = r.ping()
        print(f"✅ Redis connection successful: {result}")
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False

def test_django_setup():
    """Test Django setup."""
    print("🐍 Testing Django Setup...")
    
    try:
        from django.conf import settings
        print(f"✅ Django settings loaded successfully")
        print(f"✅ DEBUG: {settings.DEBUG}")
        print(f"✅ DATABASES: {list(settings.DATABASES.keys())}")
        return True
    except Exception as e:
        print(f"❌ Django setup failed: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 Django Auth Service - Connection Test")
    print("=" * 50)
    
    # Test environment variables
    test_environment_variables()
    
    # Test Django setup
    if not test_django_setup():
        print("❌ Django setup failed. Exiting.")
        sys.exit(1)
    
    # Test database connection
    db_ok = test_database_connection()
    
    # Test Redis connection
    redis_ok = test_redis_connection()
    
    print("=" * 50)
    print("📊 Test Results:")
    print(f"Database: {'✅ OK' if db_ok else '❌ FAILED'}")
    print(f"Redis: {'✅ OK' if redis_ok else '❌ FAILED'}")
    
    if db_ok and redis_ok:
        print("🎉 All connections successful!")
    else:
        print("🚨 Some connections failed. Check the errors above.")

if __name__ == "__main__":
    main()
