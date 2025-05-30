#!/bin/bash

# Print some logs to stdout
echo "Starting Locust container"
echo "PYTHONUNBUFFERED=$PYTHONUNBUFFERED"
echo "TARGET_HOST=$TARGET_HOST"

# Execute the original command
echo "Starting Locust with command: $@"
exec "$@"
