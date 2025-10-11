#!/bin/bash

# Start Celery Worker for OCR Processing
echo "🚀 Starting Celery worker for OCR processing..."

# Check if Redis is running
if ! pgrep -x redis-server > /dev/null; then
    echo "❌ Redis server not running. Please start Redis first."
    echo "Run: sudo systemctl start redis-server"
    exit 1
fi

# Navigate to project directory
cd /home/munga/Desktop/AI-Financial-Agent

# Activate virtual environment if not already activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "🔄 Activating virtual environment..."
    source venv-ocr/bin/activate
fi

# Check if backend directory exists
if [ ! -d "backend" ]; then
    echo "❌ Backend directory not found. Please run from project root."
    exit 1
fi

# Start Celery worker
echo "🔄 Starting Celery worker..."
cd backend
cd /home/munga/Desktop/AI-Financial-Agent && PYTHONPATH=/home/munga/Desktop/AI-Financial-Agent celery -A backend.celery_app worker --loglevel=INFO --queues=ocr_processing,batch_processing
