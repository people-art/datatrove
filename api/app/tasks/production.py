"""
Production task for full-scale dataset processing
"""

import asyncio
import uuid
import structlog
from app.worker import celery_app
from app.db.session import async_session_factory, session_factory
from app.models.benchmark import OrderStatus
from app.core.config import settings

logger = structlog.get_logger(__name__)


@celery_app.task(bind=True, name="app.tasks.production_task")
def production_task(self, order_id: str):
    """
    Async task to run full-scale dataset production with SLURM cluster.

    This task creates SLURM cluster and submits production job.
    """
    logger.info("Starting production task", order_id=order_id, task_id=self.request.id)

    try:
        # Run async SLURM cluster creation in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            result = loop.run_until_complete(_create_slurm_cluster_and_job(order_id))
            logger.info("Production task completed", order_id=order_id, result=result)
            return result

        finally:
            loop.close()

    except Exception as e:
        logger.error("Production task failed", order_id=order_id, error=str(e))
        raise self.retry(countdown=300, max_retries=5, exc=e)


async def _create_slurm_cluster_and_job(order_id: str) -> dict:
    """Create SLURM cluster and submit production job."""
    from app.services.slurm import SlurmProductionService

    # Create event loop for async operations
    loop = asyncio.get_event_loop()

    # Run SLURM production service in thread pool to avoid nested event loops
    def run_slurm_production():
        # Create new event loop for this thread
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)

        try:
            # Get order details and start SLURM production job
            from app.db.session import async_session_factory
            from app.services.order import OrderService

            async def create_production():
                async with async_session_factory() as db:
                    order_service = OrderService(db)
                    slurm_service = SlurmProductionService(order_service)

                    # Get order details
                    order = await order_service.get_order_by_id(order_id)
                    if not order or not order.benchmark_job:
                        raise Exception(f"Order or benchmark job not found: {order_id}")

                    # Start SLURM production job (this will create cluster and submit job)
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
                            "nodes": settings.SLURM_NUM_NODES,
                            "node_type": settings.SLURM_NODE_TYPE
                        }
                    }

            return new_loop.run_until_complete(create_production())

        finally:
            new_loop.close()

    # Run in thread pool to avoid event loop conflicts
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(run_slurm_production)
        result = future.result()

    return result

