"""
Benchmark job API endpoints
"""

import uuid
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.schemas import benchmark as schemas
from app.db.dependencies import get_db
from app.models.benchmark import BenchmarkJob, BenchmarkStatus
from app.services.benchmark import BenchmarkService
from app.services.pricing import PricingService
from app.core.errors import (
    AppError,
    BusinessError,
    BenchmarkError,
    ValidationError,
    handle_business_error
)

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.post("/quote", response_model=schemas.QuoteResponse)
async def create_quote(
    data: schemas.QuoteRequest,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Generate a quote for dataset generation based on requirements.
    """
    try:
        # Validate input data
        if not data.domain or not data.domain.strip():
            raise ValidationError("domain", data.domain, "Domain cannot be empty", "Please specify a domain")

        if len(data.keywords) < 2:
            raise BusinessError(
                code="BENCHMARK_TOO_FEW_KEYWORDS",
                message="Insufficient keywords provided",
                details={"hint": "Please provide at least 2 keywords to improve search accuracy"}
            )

        if len(data.keywords) > 64:
            raise ValidationError("keywords", len(data.keywords), "Too many keywords", "Maximum 64 keywords allowed")

        # Check for duplicate keywords
        unique_keywords = list(set(data.keywords))
        if len(unique_keywords) != len(data.keywords):
            logger.warning("Duplicate keywords provided", original=len(data.keywords), unique=len(unique_keywords))

        # Validate quality tier
        valid_tiers = ["basic", "standard", "premium"]
        if data.qualityTier not in valid_tiers:
            raise ValidationError("qualityTier", data.qualityTier, f"Must be one of {valid_tiers}", "Invalid quality tier selected")

        # Validate time range
        from datetime import datetime
        try:
            start_date = datetime.fromisoformat(data.startDate.replace('Z', '+00:00'))
            end_date = datetime.fromisoformat(data.endDate.replace('Z', '+00:00'))

            if end_date <= start_date:
                raise ValidationError("endDate", data.endDate, "Must be after start date", "End date must be after start date")

            # Check if date range is too large (> 5 years)
            date_diff = (end_date - start_date).days
            if date_diff > 365 * 5:
                raise BusinessError(
                    code="BENCHMARK_TIME_RANGE_TOO_LARGE",
                    message="Time range too large",
                    details={"hint": "Please reduce the date range to 5 years or less"}
                )

        except ValueError as e:
            raise ValidationError("date", f"{data.startDate} - {data.endDate}", "Invalid date format", "Please use valid ISO date format")

        # Validate languages
        if not data.languages:
            raise ValidationError("languages", data.languages, "At least one language required", "Please select at least one language")

        pricing_service = PricingService()

        # Convert request to pricing service format
        estimated_scale = None
        if data.estimatedScale and data.estimatedScale.get("docs"):
            try:
                estimated_scale = int(data.estimatedScale.get("docs"))
            except (ValueError, TypeError):
                logger.warning("Invalid estimated_scale format", value=data.estimatedScale.get("docs"))

        quote_data = await pricing_service.calculate_initial_quote(
            domain=data.domain.strip(),
            keywords=unique_keywords,
            languages=data.languages,
            time_range={
                "start": data.startDate,
                "end": data.endDate
            },
            quality_tier=data.qualityTier,
            estimated_scale=estimated_scale
        )

        # Generate quote ID and expiration
        quote_id = f"q_{uuid.uuid4().hex[:16]}"
        expires_at = "2025-12-31T23:59:59Z"  # 6 months from now (placeholder)

        logger.info(
            "Quote generated",
            quote_id=quote_id,
            domain=data.domain,
            keywords=len(unique_keywords),
            languages=data.languages,
            quality_tier=data.qualityTier
        )

        return schemas.QuoteResponse(
            quoteId=quote_id,
            currency=quote_data["currency"],
            estimate=schemas.QuoteEstimate(
                low=round(quote_data["subtotal"] * 0.8, 2),  # Conservative low estimate
                high=round(quote_data["subtotal"] * 1.2, 2)  # Conservative high estimate
            ),
            unit=schemas.QuoteUnit(
                basis="per_million_tokens",
                amount=quote_data.get("breakdown", {}).get("adjusted_price_per_million", 50.0)  # Fallback price
            ),
            expiresAt=expires_at
        )

    except (ValidationError, BusinessError) as e:
        # Re-raise custom errors
        raise
    except Exception as e:
        logger.error("Failed to generate quote", error=str(e), error_type=type(e).__name__, domain=getattr(data, 'domain', 'unknown'), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


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
