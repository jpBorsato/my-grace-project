#!/usr/bin/env bash

echo "Making database migrations..."
docker compose -f compose.yaml up -d
sleep 3
python3 manage.py makemigrations --noinput
python3 manage.py migrate --noinput

echo "Collecting static files..."
python3 manage.py collectstatic --noinput

echo "Ensuring superuser..."
python3 manage.py shell -v 0 < ensure_superuser.py

python3 manage.py runserver