#!/bin/sh
set -e

# Prepara la base, los grupos y los estaticos antes de arrancar el servidor
python manage.py migrate --noinput
python manage.py setup_groups
python manage.py collectstatic --noinput

exec "$@"
