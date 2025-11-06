"""
Benchmark task for processing dataset preview
"""

import asyncio
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from app.worker import celery_app
from app.db.dependencies import get_db
from app.services.benchmark import BenchmarkService
from app.core.config import settings

logger = structlog.get_logger(__name__)


@celery_app.task(bind=True, name="app.tasks.benchmark_task")
def benchmark_task(self, job_id: str):
    """
    Async task to run benchmark processing for dataset preview.

    This task processes a small sample (1M pages) to generate quality metrics.
    """
    logger.info("Starting benchmark task", job_id=job_id, task_id=self.request.id)

    try:
        # Run the benchmark processing
        # In production, this would integrate with the actual finewebdata pipeline
        # For now, we'll simulate processing with mock data

        # Simulate processing time (10-30 seconds)
        import time
        import random
        processing_time = random.randint(10, 30)
        time.sleep(processing_time)

        # Mock benchmark results
        mock_metrics = {
            "coverage": 0.85,
            "quality_pass_rate": 0.92,
            "pii_rate": 0.02,
            "toxicity_rate": 0.01,
            "lang_dist": {"en": 0.75, "es": 0.15, "fr": 0.05, "de": 0.03, "other": 0.02},
            "domain_dist": {"technology": 0.40, "science": 0.25, "general": 0.20, "business": 0.10, "other": 0.05}
        }

        mock_progress = {
            "pct": 100,
            "docs_read": 1000000,
            "docs_kept": 850000,
            "tokens": 85000000,
            "dedup_rate": 0.15
        }

        # Update job status in database
        # This would normally be done within the service
        logger.info("Benchmark task completed", job_id=job_id, metrics=mock_metrics)

        return {
            "status": "completed",
            "metrics": mock_metrics,
            "progress": mock_progress,
            "sample_url": f"https://storage.example.com/samples/{job_id}_sample.jsonl.gz"
        }

    except Exception as e:
        logger.error("Benchmark task failed", job_id=job_id, error=str(e))
        # Update job status to failed
        raise self.retry(countdown=60, max_retries=3, exc=e)
