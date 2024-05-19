#!/bin/bash
chmod -R 755 /media
python3 manage.py makemigrations
python3 manage.py migrate
gunicorn skin_lesions.wsgi:application --bind 0.0.0.0:8000