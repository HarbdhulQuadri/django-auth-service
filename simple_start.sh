#!/bin/bash

# Exit on any error
set -e

echo "🚀 Starting Django Auth Service..."

# Check environment variables
echo "🔍 Checking environment variables..."
if [ -z "$SECRET_KEY" ]; then
    echo "❌ SECRET_KEY not set"
    exit 1
fi

if [ -z "$DATABASE_URL" ]; then
    echo "❌ DATABASE_URL not set"
    exit 1
fi

if [ -z "$REDIS_URL" ]; then
    echo "❌ REDIS_URL not set"
    exit 1
fi

echo "✅ Environment variables are set"

# Test database connection
echo "🗄️ Testing database connection..."
python manage.py check --database default || {
    echo "❌ Database connection failed"
    echo "🔍 DATABASE_URL: ${DATABASE_URL:0:20}..."
    exit 1
}

# Run migrations
echo "🔄 Running database migrations..."
python manage.py migrate

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Start the application
echo "🚀 Starting Gunicorn server..."
exec gunicorn auth_service.wsgi:application --bind 0.0.0.0:$PORT --workers 1 --timeout 120
