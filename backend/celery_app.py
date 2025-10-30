"""
Celery Configuration for Background OCR Processing
"""
from celery import Celery
import os

# Redis configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create Celery app
celery_app = Celery(
    "financial_agent_ocr",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["backend.ocr.tasks"]
)

# Configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Africa/Nairobi",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max per task
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
)

# Task routing
celery_app.conf.task_routes = {
    'backend.ocr.tasks.process_receipt_task': {'queue': 'ocr_processing'},
    'backend.ocr.tasks.batch_process_receipts': {'queue': 'batch_processing'},
}

if __name__ == "__main__":
    celery_app.start()