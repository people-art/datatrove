"""
Benchmark service for managing benchmark jobs
"""

import json
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

from app.models.benchmark import BenchmarkJob, BenchmarkStatus
from app.core.config import settings

logger = structlog.get_logger(__name__)


class BenchmarkService:
    """Service for managing benchmark jobs."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_job(
        self,
        job_id: str,
        domain: str,
        keywords: list,
        languages: list,
        time_range_start: str,
        time_range_end: str,
        quality_tier: str,
        estimated_scale: Optional[str],
        email: str,
    ) -> BenchmarkJob:
        """Create a new benchmark job."""
        job = BenchmarkJob(
            id=job_id,
            domain=domain,
            keywords=keywords,
            languages=languages,
            time_range_start=time_range_start,
            time_range_end=time_range_end,
            quality_tier=quality_tier,
            estimated_scale=estimated_scale,
            email=email,
            status=BenchmarkStatus.QUEUED,
        )

        self.db.add(job)
        await self.db.flush()  # Get the job ID without committing

        return job

    async def get_job(self, job_id: str) -> Optional[BenchmarkJob]:
        """Get benchmark job by ID."""
        stmt = select(BenchmarkJob).where(BenchmarkJob.id == job_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def update_job_status(
        self,
        job_id: str,
        status: BenchmarkStatus,
        error_message: Optional[str] = None,
        **kwargs
    ) -> None:
        """Update benchmark job status and metadata."""
        job = await self.get_job(job_id)
        if not job:
            return

        job.status = status
        if error_message:
            job.error_message = error_message

        # Update progress/metrics fields
        for key, value in kwargs.items():
            if hasattr(job, key):
                setattr(job, key, value)

        await self.db.commit()

    async def start_benchmark_task(self, job_id: str) -> None:
        """Start benchmark task (placeholder - will be implemented with Celery)."""
        # TODO: Integrate with Celery for async task processing
        # For now, we'll simulate the benchmark process

        logger.info("Starting benchmark task", job_id=job_id)

        # Update status to running
        await self.update_job_status(job_id, BenchmarkStatus.RUNNING)

        # TODO: Call actual benchmark logic here
        # This would typically involve:
        # 1. Creating a finewebdata.py job with benchmark parameters
        # 2. Processing sample data
        # 3. Updating progress and metrics
        # 4. Generating sample download URL

        # Simulate completion for development
        await self._simulate_benchmark_completion(job_id)

    async def _simulate_benchmark_completion(self, job_id: str) -> None:
        """Simulate benchmark completion for development."""
        import asyncio
        import random

        # Simulate processing time
        await asyncio.sleep(5)

        # Update with mock results
        await self.update_job_status(
            job_id,
            BenchmarkStatus.READY,
            progress_pct=100.0,
            docs_read=settings.BENCHMARK_SAMPLE_SIZE,
            docs_kept=int(settings.BENCHMARK_SAMPLE_SIZE * 0.85),
            tokens=int(settings.BENCHMARK_SAMPLE_SIZE * 0.85 * 250),  # ~250 tokens per doc
            dedup_rate=0.15,
            coverage=0.82,
            quality_pass_rate=0.88,
            pii_rate=0.003,
            toxicity_rate=0.005,
            lang_dist={"en": 850000, "es": 50000, "fr": 30000, "de": 20000},
            domain_dist={"technology": 200000, "science": 150000, "business": 100000, "health": 80000},
            sample_url=f"https://s3.amazonaws.com/{settings.S3_BUCKET_SAMPLES}/benchmark-{job_id}-sample.jsonl.gz",
            suggested_params={
                "thresholds": {"domain": 3, "quality": 2},
                "filters": {"min_words": 100, "max_pii_score": 0.1}
            }
        )

        logger.info("Benchmark task completed", job_id=job_id)

    async def calculate_quote(self, job_id: str) -> Dict[str, Any]:
        """Calculate pricing quote based on benchmark results."""
        job = await self.get_job(job_id)
        if not job or job.status != BenchmarkStatus.READY:
            raise ValueError("Benchmark job not ready for quoting")

        # Base pricing logic
        base_price_per_million_tokens = 50.0  # $50 per million tokens

        # Quality tier multipliers
        quality_multipliers = {
            "basic": 0.8,
            "standard": 1.0,
            "premium": 1.5,
        }

        # Estimate final dataset size based on benchmark
        if job.tokens > 0:
            estimated_final_tokens = job.tokens * 100  # Scale up from 1M to 100M sample
            quality_multiplier = quality_multipliers.get(job.quality_tier, 1.0)

            subtotal = (estimated_final_tokens / 1_000_000) * base_price_per_million_tokens * quality_multiplier
            tax_rate = 0.08  # 8% tax
            tax = subtotal * tax_rate
            total = subtotal + tax

            pricing_notes = (
                f"Estimated {estimated_final_tokens:,} tokens based on benchmark coverage. "
                f"Quality tier '{job.quality_tier}' applied. "
                "Final price may vary based on actual processing results."
            )
        else:
            # Fallback pricing
            subtotal = 500.0
            tax = 40.0
            total = 540.0
            pricing_notes = "Default pricing - benchmark results unavailable."

        return {
            "currency": "USD",
            "subtotal": round(subtotal, 2),
            "tax": round(tax, 2),
            "total": round(total, 2),
            "pricing_notes": pricing_notes,
        }
