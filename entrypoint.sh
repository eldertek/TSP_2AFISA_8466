#!/bin/sh
set -e

python manage.py migrate --noinput
python manage.py collectstatic --noinput

export DJANGO_SUPERUSER_USERNAME="admin"
export DJANGO_SUPERUSER_EMAIL="admin@intetes.local"
export DJANGO_SUPERUSER_PASSWORD="projetinfo1A"

python manage.py createsuperuser --noinput || true

exec "$@"