#!/bin/bash

# ALCHEMY - Temporal Content Transmuter
# Startup Script

set -e

echo "🌐 ALCHEMY - Temporal Content Transmuter"
echo "======================================"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"
echo ""

# Create necessary directories
echo "Creating directories..."
mkdir -p raw_ore processed_gold logs
echo "✓ Directories created"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "✓ .env file created"
    echo "⚠️  Please review and update .env with your configuration"
    echo ""
fi

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Initialize database
echo "Initializing database..."
python3 -c "from src.api.database import init_db; init_db()"
echo "✓ Database initialized"
echo ""

# Validate settings
echo "Validating settings..."
python3 -c "from src.api.config import validate_settings; validate_settings() and print('✓ Settings validated') or print('✗ Settings validation failed')"
echo ""

# Start API server
echo "Starting API server..."
echo "API will be available at: http://localhost:8000"
echo "API documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
