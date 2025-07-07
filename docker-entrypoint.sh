#!/bin/sh

trap 'exit' INT TERM
trap 'kill 0' EXIT

echo "Waiting for PostgreSQL to be ready..."

until nc -z pgdb_new 5432; do
  echo "Waiting for PostgreSQL..."
  sleep 1
done

echo "PostgreSQL is ready."


echo "Updating poetry.."
poetry update

echo "Running migrations with Poetry..."
poetry run python manage.py makemigrations
poetry run python manage.py migrate --noinput
echo "Migrations done."

echo "Starting Django application..."
exec poetry run python manage.py runserver 0.0.0.0:8000
