#!/bin/bash

# Load environment variables
set -a
source .env
set +a

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Start the application with production settings
echo "Starting the application..."
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
