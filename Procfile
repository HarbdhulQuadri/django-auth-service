web: python manage.py migrate && gunicorn auth_service.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
