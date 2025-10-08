#!/usr/bin/env bash

echo "Installing project dependencies..."
python3 -m pip install -r -requirements.txt

echo "Making database migrations..."
python3 manage.py makemigrations --noinput
python3 manage.py migrate --noinput

echo "Collecting static files..."
python3 manage.py collectstatic --noinput