#!/bin/bash

# Standalone FastAPI Backend Startup Script
# This script starts the standalone AI Financial Agent backend

echo "Starting AI Financial Agent - Standalone Backend..."
echo "========================================"

# Check if we're in the correct directory
if [ ! -f "standalone_app.py" ]; then
    echo "Error: standalone_app.py not found. Please run this script from the backend directory."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r standalone_requirements.txt

# Set environment variables if not already set
export ENVIRONMENT=${ENVIRONMENT:-development}
export PORT=${PORT:-8002}
export MONGO_URI=${MONGO_URI:-mongodb://localhost:27017}
export DATABASE_NAME=${DATABASE_NAME:-kenya_fintech_suite}
export GEMINI_API_KEY=${GEMINI_API_KEY:-your-api-key}
export GEMINI_MODEL=${GEMINI_MODEL:-gemini-1.5-pro}

echo "Environment variables:"
echo "  ENVIRONMENT: $ENVIRONMENT"
echo "  PORT: $PORT"
echo "  MONGO_URI: $MONGO_URI"
echo "  DATABASE_NAME: $DATABASE_NAME"
echo "  GEMINI_MODEL: $GEMINI_MODEL"

echo ""
echo "Starting server on port $PORT..."
echo "API Documentation: http://localhost:$PORT/docs"
echo "Health Check: http://localhost:$PORT/health"
echo "AI Query Endpoint: http://localhost:$PORT/ai/ask"
echo ""

# Start the server
python standalone_app.py
