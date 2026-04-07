#!/bin/bash
set -e

python manage.py migrate --noinput
python manage.py createsuperuser --noinput 2>/dev/null || true
python manage.py load_mock_data
python manage.py runserver 0.0.0.0:8000
