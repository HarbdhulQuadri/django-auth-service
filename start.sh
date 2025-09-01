#!/bin/bash

echo "Starting Django Auth Service..."

# Wait for database to be ready
echo "Waiting for database..."
python manage.py wait_for_db

# Run migrations
echo "Running database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start Gunicorn
echo "Starting Gunicorn server..."
exec gunicorn auth_service.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 1 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
