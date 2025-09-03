#!/bin/sh

echo "Waiting for MySQL at $DB_HOST..."

# Wait until MySQL is reachable
until mysqladmin ping -h "$DB_HOST" --silent; do
  echo "Waiting for database connection..."
  sleep 2
done

echo "Database ready, running migrations..."
python manage.py migrate

echo "Creating superuser if it doesn't exist..."
python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
username = '${DJANGO_SUPERUSER_USERNAME}'
email = '${DJANGO_SUPERUSER_EMAIL}'
password = '${DJANGO_SUPERUSER_PASSWORD}'

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
END

echo "Starting Django development server..."
# Use exec so signals are forwarded properly
exec python manage.py runserver 0.0.0.0:8000
# For production, replace the above line with:
# exec gunicorn app.wsgi:application --bind