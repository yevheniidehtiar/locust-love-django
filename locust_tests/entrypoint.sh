#!/bin/bash

# Print some logs to stdout
echo "Starting Locust container"
echo "PYTHONUNBUFFERED=$PYTHONUNBUFFERED"
echo "TARGET_HOST=$TARGET_HOST"

# Run the startup logger script
echo "Running startup_logger.py"
python /app/startup_logger.py

# Execute the original command
echo "Starting Locust with command: $@"
exec "$@"
