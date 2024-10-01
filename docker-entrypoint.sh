#!/bin/sh

# process signals
trap 'exit' INT TERM
trap 'kill 0' EXIT

echo "Waiting for PostgreSQL..."
while ! nc -z pgdb 5432; do
  sleep 0.1
done
echo "Done with PostgreSQL"

echo "Running migrations with poetry"
poetry run python todo/manage.py migrate
echo "Done with migrations"

exec poetry run python todo/manage.py runserver 0.0.0.0:8000