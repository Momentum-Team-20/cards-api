#!/usr/bin/env bash
# exit on error
set -o errexit

python manage.py migrate
python manage.py collectstatic --no-input
