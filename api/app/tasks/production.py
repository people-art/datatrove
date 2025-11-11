"""
Production task for full-scale dataset processing
"""

import asyncio
import structlog
from app.worker import celery_app
from app.db.session import async_session_factory

logger = structlog.get_logger(__name__)


@celery_app.task(bind=True, name="app.tasks.production_task")
def production_task(self, order_id: str):
    """
    Async task to run full-scale dataset production.

    This task processes the complete dataset and uploads to Hugging Face.
    """
    logger.info("Starting production task", order_id=order_id, task_id=self.request.id)

    try:
        # Run async SLURM job submission in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            # Get order details and start SLURM production job
            result = loop.run_until_complete(_start_slurm_production(order_id))
            logger.info("Production task completed", order_id=order_id, result=result)
            return result

        finally:
            loop.close()

    except Exception as e:
        logger.error("Production task failed", order_id=order_id, error=str(e))
        raise self.retry(countdown=300, max_retries=5, exc=e)


async def _start_slurm_production(order_id: str) -> dict:
    """Start SLURM production job for the order."""

    async with async_session_factory() as db:
        # Import here to avoid circular imports
        from app.services.order import OrderService
        from app.services.slurm import SlurmProductionService

        order_service = OrderService(db)
        slurm_service = SlurmProductionService(order_service)

        # Get order details
        order = await order_service.get_order_by_id(order_id)
        if not order or not order.benchmark_job:
            raise Exception(f"Order or benchmark job not found: {order_id}")

        # Start SLURM production job
        slurm_job_id = await slurm_service.start_production_job(
            order_id=order_id,
            benchmark_job_id=order.benchmark_job.id,
            domain=order.benchmark_job.domain,
            keywords=order.benchmark_job.keywords,
            languages=order.benchmark_job.languages,
            time_range_start=order.benchmark_job.time_range_start,
            time_range_end=order.benchmark_job.time_range_end,
            quality_tier=order.benchmark_job.quality_tier,
        )

        return {
            "status": "slurm_job_submitted",
            "slurm_job_id": slurm_job_id,
            "cluster_info": {
                "nodes": 5,  # Default from config
                "node_type": "t3.xlarge"
            }
        }
