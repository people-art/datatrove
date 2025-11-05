"""
Benchmark job API endpoints
"""

import uuid
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app import schemas
from app.db.dependencies import get_db
from app.models.benchmark import BenchmarkJob, BenchmarkStatus
from app.services.benchmark import BenchmarkService

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.post("/jobs", response_model=schemas.BenchmarkJobCreateResponse)
async def create_benchmark_job(
    data: schemas.DomainFormData,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Create a new benchmark job for preview generation.
    """
    try:
        job_id = str(uuid.uuid4())

        # Create benchmark job record
        benchmark_service = BenchmarkService(db)
        job = await benchmark_service.create_job(
            job_id=job_id,
            domain=data.domain,
            keywords=data.keywords,
            languages=data.languages,
            time_range_start=data.time_range["start"],
            time_range_end=data.time_range["end"],
            quality_tier=data.quality_tier,
            estimated_scale=data.estimated_scale,
            email=data.email,
        )

        # Start benchmark task asynchronously
        await benchmark_service.start_benchmark_task(job_id)

        logger.info("Benchmark job created", job_id=job_id, domain=data.domain)

        return schemas.BenchmarkJobCreateResponse(jobId=job_id)

    except Exception as e:
        logger.error("Failed to create benchmark job", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create benchmark job")


@router.get("/jobs/{job_id}", response_model=schemas.BenchmarkJobResponse)
async def get_benchmark_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get benchmark job status and results.
    """
    try:
        benchmark_service = BenchmarkService(db)
        job = await benchmark_service.get_job(job_id)

        if not job:
            raise HTTPException(status_code=404, detail="Benchmark job not found")

        # Convert to response schema
        progress = None
        if job.status in [BenchmarkStatus.RUNNING, BenchmarkStatus.READY]:
            progress = schemas.BenchmarkProgress(
                pct=job.progress_pct,
                docs_read=job.docs_read,
                docs_kept=job.docs_kept,
                tokens=job.tokens,
                dedup_rate=job.dedup_rate,
            )

        metrics = None
        if job.status == BenchmarkStatus.READY and all([
            job.coverage is not None,
            job.quality_pass_rate is not None,
            job.pii_rate is not None,
            job.toxicity_rate is not None,
        ]):
            metrics = schemas.BenchmarkMetrics(
                coverage=job.coverage,
                quality_pass_rate=job.quality_pass_rate,
                pii_rate=job.pii_rate,
                toxicity_rate=job.toxicity_rate,
                lang_dist=job.lang_dist or {},
                domain_dist=job.domain_dist or {},
            )

        return schemas.BenchmarkJobResponse(
            id=job.id,
            status=job.status.value,
            progress=progress,
            metrics=metrics,
            sample_url=job.sample_url,
            suggested_params=job.suggested_params,
            error=job.error_message,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get benchmark job", job_id=job_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get benchmark job")


@router.post("/quote", response_model=schemas.QuoteResponse)
async def get_quote(
    request: schemas.QuoteRequest,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get pricing quote for a completed benchmark job.
    """
    try:
        benchmark_service = BenchmarkService(db)
        quote = await benchmark_service.calculate_quote(request.jobId)

        return schemas.QuoteResponse(
            currency=quote["currency"],
            subtotal=quote["subtotal"],
            tax=quote["tax"],
            total=quote["total"],
            pricing_notes=quote["pricing_notes"],
        )

    except Exception as e:
        logger.error("Failed to get quote", job_id=request.jobId, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to calculate quote")
