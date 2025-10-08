#!/usr/bin/env bash

echo "Making database migrations..."
python3 manage.py makemigrations --noinput
python3 manage.py migrate --noinput

echo "Collecting static files..."
python3 manage.py collectstatic --noinput

docker compose -f compose.yaml up -d

python3 manage.py runserver