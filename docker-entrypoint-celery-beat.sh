#!/bin/bash

echo "Checking if celery is installed..."
/todo/.venv/bin/celery --version || { echo "Celery not found! Exiting..."; exit 1; }

until cd /app; do
  echo "Waiting for server volume..."
  sleep 1
done

echo "Activating virtual environment..."
source /todo/.venv/bin/activate || { echo "Failed to activate virtual environment"; exit 1; }

echo "Starting Celery Beat..."
/todo/.venv/bin/celery -A todo beat -l info || { echo "Failed to start Celery Beat!"; exit 1; }
