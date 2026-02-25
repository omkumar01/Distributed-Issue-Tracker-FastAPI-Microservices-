#!/bin/bash
# Setup local development environment

set -e

echo "Setting up development environment..."

# Copy .env file
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✓ Created .env file (remember to update with your settings)"
else
    echo "✓ .env file already exists"
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r shared/requirements.txt

# Install service dependencies
for service in services/*/; do
    if [ -f "$service/requirements.txt" ]; then
        echo "Installing $(basename $service) dependencies..."
        pip install -r "$service/requirements.txt"
    fi
done

echo "✓ Dependencies installed"

# Build Docker images
echo "Building Docker images..."
docker-compose build

echo "✓ Docker images built"

echo ""
echo "Setup complete! You can now start the services with:"
echo "  make up         # Start all services"
echo "  make logs       # View service logs"
echo "  make test       # Run tests"
echo ""
