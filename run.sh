#!/bin/sh
echo "Running migrations..."
python manage.py makemigrations;
python manage.py migrate;

echo "Collecting static files..."
python manage.py collectstatic --noinput;

echo "Starting Celery worker..."
celery -A alfa_people worker -l info --pool=solo &

echo "Starting Celery beat..."
celery -A alfa_people beat --loglevel=info &

echo "Loading initial data..."
python manage.py loaddata user_dump.json;
python manage.py update_users;
python manage.py loaddata other_dump.json;

echo "Copying static files..."
cp -r /app/collected_static/. /backend_static/static/

echo "Starting Gunicorn..."
gunicorn --bind 0:8000 alfa_people.wsgi;