#!/bin/bash

# Exit on any error
set -e

echo "Starting Django Auth Service..."

# Wait for database to be ready (if needed)
echo "Checking database connection..."
python manage.py check --database default

# Run migrations
echo "Running database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start the application
echo "Starting Gunicorn server..."
exec gunicorn auth_service.wsgi:application --bind 0.0.0.0:$PORT --workers 1 --timeout 120
