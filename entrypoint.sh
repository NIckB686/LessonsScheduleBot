#!/bin/sh
set -e

echo "Waiting for Postgres..."
until alembic current; do
    echo "Postgres is unavailable - sleeping"
    sleep 30
done

echo "Running migrations..."
alembic upgrade head

echo "Starting bot..."
exec python main.py
