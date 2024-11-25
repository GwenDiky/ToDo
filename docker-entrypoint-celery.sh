#!/bin/bash

echo "Checking if celery is installed..."
which celery

until cd /app
do
  echo "Waiting for server volume"
  sleep 1
done

source /todo/.venv/bin/activate

echo "Starting celery worker..."
celery -A todo worker -l info --concurrency 1 -E

