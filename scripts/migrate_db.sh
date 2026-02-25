#!/bin/bash
# Database migration script

set -e

echo "Running database migrations..."

# Apply Alembic migrations
docker-compose exec auth-service alembic upgrade head

echo "Migrations completed successfully!"
