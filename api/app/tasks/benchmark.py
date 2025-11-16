"""
Benchmark task for processing dataset preview
"""

import asyncio
import os
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from app.worker import celery_app
from app.db.dependencies import get_db
from app.services.benchmark import BenchmarkService
from app.services.finewebdata_service import FineWebDataService, BenchmarkConfig
from app.core.config import settings

logger = structlog.get_logger(__name__)


async def _update_job_status(job_id: str, mock_progress: dict, mock_metrics: dict):
    """Helper function to update job status asynchronously."""
    from app.db.session import async_session_factory
    from app.services.benchmark import BenchmarkService
    from app.models.benchmark import BenchmarkStatus
    import asyncio

    # Add retry logic for database operations
    max_retries = 3
    for attempt in range(max_retries):
        try:
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
                    sample_url=f"https://s3.amazonaws.com/{settings.S3_BUCKET_SAMPLES}/benchmark-{job_id}-sample.jsonl.gz",
                    suggested_params={
                        "thresholds": {"domain": 3, "quality": 2},
                        "filters": {"min_words": 100, "max_pii_score": 0.1}
                    }
                )
            return  # Success, exit retry loop
        except Exception as e:
            if attempt == max_retries - 1:  # Last attempt
                raise e
            # Wait before retrying
            await asyncio.sleep(1 * (attempt + 1))  # Exponential backoff: 1s, 2s, 3s


@celery_app.task(bind=True, name="app.tasks.benchmark_task")
def benchmark_task(self, job_id: str):
    """
    Async task to run benchmark processing for dataset preview.

    This task processes a small sample (1M pages) to generate quality metrics.
    """
    logger.info("Starting benchmark task", job_id=job_id, task_id=self.request.id)

    try:
        # Get benchmark job configuration
        job_config = get_job_config(job_id)
        if not job_config:
            raise Exception(f"Benchmark job not found: {job_id}")

        # Create benchmark config
        benchmark_config = BenchmarkConfig(
            job_id=job_id,
            domain=job_config["domain"],
            keywords=job_config["keywords"],
            languages=job_config["languages"],
            time_range_start=job_config["time_range_start"],
            time_range_end=job_config["time_range_end"],
            quality_tier=job_config["quality_tier"],
            estimated_scale=job_config.get("estimated_scale")
        )

        # Run benchmark pipeline using FineWebData service
        finewebdata_service = FineWebDataService()
        result = asyncio.run(finewebdata_service.run_benchmark_pipeline(benchmark_config))

        # Convert BenchmarkResult to dict for database operations
        result_dict = {
            "docs_read": result.docs_read,
            "docs_kept": result.docs_kept,
            "tokens": result.tokens,
            "dedup_rate": result.dedup_rate,
            "coverage": result.coverage,
            "quality_pass_rate": result.quality_pass_rate,
            "pii_rate": result.pii_rate,
            "toxicity_rate": result.toxicity_rate,
            "lang_dist": result.lang_dist,
            "domain_dist": result.domain_dist,
            "sample_url": result.sample_url,
            "suggested_params": result.suggested_params,
        }

        # Update job status in database
        asyncio.run(update_job_status_with_result(job_id, result))

        # Always try to upload benchmark sample to S3
        sample_url = asyncio.run(upload_benchmark_sample_to_s3(job_id, result))
        if sample_url:
            asyncio.run(update_sample_url(job_id, sample_url))
            # Update the result_dict with the actual sample URL
            result_dict["sample_url"] = sample_url

        logger.info("Benchmark task completed successfully", job_id=job_id)

        return {
            "status": "completed",
            "metrics": {
                "coverage": result.coverage,
                "quality_pass_rate": result.quality_pass_rate,
                "pii_rate": result.pii_rate,
                "toxicity_rate": result.toxicity_rate,
                "lang_dist": result.lang_dist,
                "domain_dist": result.domain_dist,
            },
            "progress": {
                "pct": 100,
                "docs_read": result.docs_read,
                "docs_kept": result.docs_kept,
                "tokens": result.tokens,
                "dedup_rate": result.dedup_rate
            },
            "sample_url": result.sample_url
        }

    except Exception as e:
        logger.error("Benchmark task failed", job_id=job_id, error=str(e))

        # Update job status to failed
        try:
            asyncio.run(update_job_status_failed(job_id, str(e)))
        except Exception as db_error:
            logger.error("Failed to update job status to failed", job_id=job_id, error=str(db_error))

        # Retry with exponential backoff
        raise self.retry(countdown=60, max_retries=3, exc=e)


def get_job_config(job_id: str) -> dict:
    """Get benchmark job configuration from database"""
    from app.db.session import session_factory
    from app.models.benchmark import BenchmarkJob
    from sqlalchemy import select

    with session_factory() as db:
        stmt = select(BenchmarkJob).where(BenchmarkJob.id == job_id)
        result = db.execute(stmt)
        job = result.scalar_one_or_none()

        if not job:
            return None

        return {
            "domain": job.domain,
            "keywords": job.keywords,
            "languages": job.languages,
            "time_range_start": job.time_range_start,
            "time_range_end": job.time_range_end,
            "quality_tier": job.quality_tier,
            "estimated_scale": job.estimated_scale,
        }


async def update_job_status_with_result(job_id: str, result):
    """Update job status with benchmark results"""
    from app.db.session import async_session_factory
    from app.services.benchmark import BenchmarkService
    from app.models.benchmark import BenchmarkStatus

    max_retries = 3
    for attempt in range(max_retries):
        try:
            async with async_session_factory() as db:
                benchmark_service = BenchmarkService(db)
                await benchmark_service.update_job_status(
                    job_id=job_id,
                    status=BenchmarkStatus.READY,
                    progress_pct=100.0,
                    docs_read=result.docs_read,
                    docs_kept=result.docs_kept,
                    tokens=result.tokens,
                    dedup_rate=result.dedup_rate,
                    coverage=result.coverage,
                    quality_pass_rate=result.quality_pass_rate,
                    pii_rate=result.pii_rate,
                    toxicity_rate=result.toxicity_rate,
                    lang_dist=result.lang_dist,
                    domain_dist=result.domain_dist,
                    sample_url=result.sample_url,
                    suggested_params=result.suggested_params,
                )
            return  # Success, exit retry loop
        except Exception as e:
            if attempt == max_retries - 1:  # Last attempt
                raise e
            # Wait before retrying
            await asyncio.sleep(1 * (attempt + 1))  # Exponential backoff: 1s, 2s, 3s


async def update_job_status_failed(job_id: str, error_message: str):
    """Update job status to failed"""
    from app.db.session import async_session_factory
    from app.services.benchmark import BenchmarkService
    from app.models.benchmark import BenchmarkStatus

    try:
        async with async_session_factory() as db:
            benchmark_service = BenchmarkService(db)
            await benchmark_service.update_job_status(
                job_id=job_id,
                status=BenchmarkStatus.FAILED,
                error_message=error_message,
            )
    except Exception as e:
        logger.error("Failed to update job status to failed", job_id=job_id, error=str(e))
        raise


async def upload_benchmark_sample_to_s3(job_id: str, result) -> str:
    """
    Upload benchmark sample data to S3.

    Args:
        job_id: Benchmark job ID
        result: Benchmark result object or dict containing sample_documents

    Returns:
        str: S3 URL of uploaded sample
    """
    import boto3
    import gzip
    import json
    import tempfile
    from app.core.config import settings

    try:
        # Extract sample documents from result
        sample_documents = None

        # Handle both BenchmarkResult object and dict formats
        if hasattr(result, 'sample_documents'):
            sample_documents = result.sample_documents
        elif isinstance(result, dict) and 'sample_documents' in result:
            sample_documents = result['sample_documents']

        if not sample_documents:
            logger.warning("No sample documents found in benchmark result", job_id=job_id)
            return None

        # Create temporary JSONL file
        with tempfile.NamedTemporaryFile(mode='w+b', suffix='.jsonl.gz', delete=False) as temp_file:
            temp_file_path = temp_file.name

            # Write sample documents as JSONL (one JSON per line)
            with gzip.open(temp_file, 'wt', encoding='utf-8') as gz_file:
                for doc in sample_documents[:100]:  # Limit to 100 samples for download size
                    json_line = json.dumps(doc, ensure_ascii=False)
                    gz_file.write(json_line + '\n')

        try:
            # Upload to S3
            s3_client = boto3.client('s3')
            s3_key = f"benchmark-{job_id}-sample.jsonl.gz"

            with open(temp_file_path, 'rb') as f:
                s3_client.upload_fileobj(f, settings.S3_BUCKET_SAMPLES, s3_key)

            s3_url = f"https://s3.amazonaws.com/{settings.S3_BUCKET_SAMPLES}/{s3_key}"
            logger.info("Benchmark sample uploaded to S3", job_id=job_id, s3_url=s3_url, sample_count=len(sample_documents))

            return s3_url

        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)

    except Exception as e:
        logger.error("Failed to upload benchmark sample to S3", job_id=job_id, error=str(e))
        return None


async def update_sample_url(job_id: str, sample_url: str):
    """
    Update the sample URL for a benchmark job.

    Args:
        job_id: Benchmark job ID
        sample_url: New sample URL
    """
    from app.db.session import async_session_factory
    from app.services.benchmark import BenchmarkService

    try:
        async with async_session_factory() as db:
            benchmark_service = BenchmarkService(db)
            await benchmark_service.update_job_status(
                job_id=job_id,
                sample_url=sample_url,
            )
        logger.info("Sample URL updated", job_id=job_id, sample_url=sample_url)
    except Exception as e:
        logger.error("Failed to update sample URL", job_id=job_id, error=str(e))
