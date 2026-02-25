#!/bin/bash
# Seed database with sample data

set -e

echo "Seeding database with sample data..."

# Run Python seed script
docker-compose exec auth-service python -m scripts.seed_database

echo "Seeding completed successfully!"
