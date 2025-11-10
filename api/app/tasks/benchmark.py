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


async def _update_job_status(job_id: str, mock_progress: dict, mock_metrics: dict):
    """Helper function to update job status asynchronously."""
    from app.db.session import async_session_factory
    from app.services.benchmark import BenchmarkService
    from app.models.benchmark import BenchmarkStatus

    async with async_session_factory() as db:
        benchmark_service = BenchmarkService(db)
        await benchmark_service.update_job_status(
            job_id=job_id,
            status=BenchmarkStatus.READY,
            progress_pct=mock_progress["pct"],
            docs_read=mock_progress["docs_read"],
            docs_kept=mock_progress["docs_kept"],
            tokens=mock_progress["tokens"],
            dedup_rate=mock_progress["dedup_rate"],
            coverage=mock_metrics["coverage"],
            quality_pass_rate=mock_metrics["quality_pass_rate"],
            pii_rate=mock_metrics["pii_rate"],
            toxicity_rate=mock_metrics["toxicity_rate"],
            lang_dist=mock_metrics["lang_dist"],
            domain_dist=mock_metrics["domain_dist"],
            sample_url=f"https://s3.amazonaws.com/finedata-dev-samples/benchmark-{job_id}-sample.jsonl.gz",
            suggested_params={
                "thresholds": {"domain": 3, "quality": 2},
                "filters": {"min_words": 100, "max_pii_score": 0.1}
            }
        )


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
            "lang_dist": {"en": 637500, "es": 127500, "fr": 42500, "de": 25500, "other": 17000},
            "domain_dist": {"technology": 340000, "science": 212500, "general": 170000, "business": 85000, "other": 42500}
        }

        mock_progress = {
            "pct": 100,
            "docs_read": 1000000,
            "docs_kept": 850000,
            "tokens": 85000000,
            "dedup_rate": 0.15
        }

        # Update job status in database
        # Run async database update in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(_update_job_status(
                job_id=job_id,
                mock_progress=mock_progress,
                mock_metrics=mock_metrics
            ))
        finally:
            loop.close()

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
