"""
Celery worker configuration for async task processing
"""

from celery import Celery
from app.core.config import settings

# Configure Celery
celery_app = Celery(
    "finedata_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_routes={
        "app.tasks.benchmark_task": {"queue": "benchmark"},
        "app.tasks.production_task": {"queue": "production"},
        "app.tasks.email_task": {"queue": "email"},
    },
    task_default_queue="default",
    task_default_exchange="finedata",
    task_default_routing_key="finedata",
    worker_prefetch_multiplier=1,  # One task per worker at a time
    task_acks_late=True,  # Tasks are acknowledged after completion
    worker_disable_rate_limits=False,
    task_annotations={
        "*": {
            "rate_limit": "10/m",  # Global rate limit
        }
    }
)

if __name__ == "__main__":
    celery_app.start()
