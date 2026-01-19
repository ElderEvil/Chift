#!/bin/bash

# Chift Setup Script
# This script helps you set up the Chift application quickly

set -e

echo "================================================"
echo "  Chift - Odoo Integration API Setup"
echo "================================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file with your Odoo credentials before starting!"
    echo ""
else
    echo "✓ .env file already exists"
    echo ""
fi

# Check if Docker is installed
if command -v docker &> /dev/null; then
    echo "✓ Docker is installed"

    # Ask user if they want to use Docker
    read -p "Do you want to run with Docker Compose? (y/n): " use_docker

    if [ "$use_docker" = "y" ] || [ "$use_docker" = "Y" ]; then
        echo ""
        echo "Starting application with Docker Compose..."
        docker-compose up -d
        echo ""
        echo "✓ Application started!"
        echo ""
        echo "API is now running at: http://localhost:8000"
        echo "API Documentation: http://localhost:8000/docs"
        echo ""
        echo "To view logs: docker-compose logs -f"
        echo "To stop: docker-compose down"
        exit 0
    fi
fi

# Local setup
echo ""
echo "Setting up local environment..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.13+ first."
    exit 1
fi

echo "✓ Python is installed"

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    pip install uv
    echo "✓ uv installed"
else
    echo "✓ uv is installed"
fi

# Install dependencies
echo ""
echo "Installing dependencies..."
uv sync
echo "✓ Dependencies installed"

# Check if PostgreSQL is running
echo ""
echo "⚠️  Make sure PostgreSQL is running and DATABASE_URL in .env is correct!"
echo ""

# Run migrations
read -p "Do you want to run database migrations now? (y/n): " run_migrations

if [ "$run_migrations" = "y" ] || [ "$run_migrations" = "Y" ]; then
    echo ""
    echo "Running database migrations..."
    uv run alembic upgrade head
    echo "✓ Migrations completed"
fi

echo ""
echo "================================================"
echo "  Setup Complete!"
echo "================================================"
echo ""
echo "To start the application:"
echo "  uv run uvicorn main:app --reload"
echo ""
echo "The API will be available at: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo ""
echo "Default credentials:"
echo "  Username: admin"
echo "  Password: secret"
echo ""
