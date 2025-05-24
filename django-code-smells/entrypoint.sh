#!/bin/bash
set -e

# Print some logs to stdout
echo "Starting Django container"
echo "PYTHONUNBUFFERED=$PYTHONUNBUFFERED"
echo "DEBUG=$DEBUG"

# Function to run migrations
run_migrations() {
    echo "Running migrations..."
    python manage.py migrate
}

# Function to collect static files
collect_static() {
    echo "Collecting static files..."
    python manage.py collectstatic --noinput
}

# Check if we need to run migrations
if [ "$1" = "migrate" ]; then
    run_migrations
    exit 0
fi

# Check if we need to collect static files
if [ "$1" = "collectstatic" ]; then
    collect_static
    exit 0
fi

# Check if we need to run both migrations and collect static before starting the server
if [ "$1" = "start" ]; then
    run_migrations
    collect_static
    echo "Starting Django server..."
    exec python manage.py runserver 0.0.0.0:8000
fi

# If a command is provided, execute it
if [ "$1" != "" ]; then
    echo "Running command: $@"
    exec "$@"
else
    # Default: start the Django server
    echo "Starting Django server..."
    exec python manage.py runserver 0.0.0.0:8000
fi