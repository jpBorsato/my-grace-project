#!/usr/bin/env bash

echo "Making database migrations..."
docker compose -f compose.yaml up -d
python3 manage.py makemigrations --noinput
python3 manage.py migrate --noinput

echo "Collecting static files..."
python3 manage.py collectstatic --noinput

python3 manage.py runserver