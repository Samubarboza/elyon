#!/bin/sh
set -e

# Prepara la base y los grupos antes de arrancar el servidor
python manage.py migrate --noinput
python manage.py setup_groups

exec "$@"
