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
    Celery task to run full-scale dataset production with SLURM cluster.

    This task creates SLURM cluster and submits production job.
    """
    logger.info("Starting production task", order_id=order_id, task_id=self.request.id)

    try:
        # Use synchronous database operations for Celery compatibility
        from app.db.session import session_factory
        from app.models.benchmark import Order, OrderStatus, OrderTimelineEvent
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        import uuid

        # Use sync database session
        with session_factory() as db:
            # Get order details with joined benchmark job
            stmt = select(Order).options(selectinload(Order.benchmark_job)).where(Order.id == order_id)
            result = db.execute(stmt)
            order = result.scalar_one_or_none()

            if not order or not order.benchmark_job:
                raise Exception(f"Order or benchmark job not found: {order_id}")

            # Update order status to cluster queued
            cluster_name = f"production-{uuid.uuid4().hex[:8]}"
            order.status = OrderStatus.CLUSTER_QUEUED
            order.cluster_name = cluster_name
            db.commit()

            # Add timeline event
            timeline_event = OrderTimelineEvent(
                order_id=order_id,
                event_type="status_change",
                description=f"Order status changed from {OrderStatus.PAID} to {OrderStatus.CLUSTER_QUEUED}",
                event_metadata={"cluster_name": cluster_name}
            )
            db.add(timeline_event)
            db.commit()

            # Mock SLURM cluster creation and job submission
            # In production, this would actually create SLURM cluster
            slurm_job_id = f"slurm-{uuid.uuid4().hex[:8]}"

            # Update to running status
            order.status = OrderStatus.RUNNING
            order.slurm_job_id = slurm_job_id
            db.commit()

            # Add another timeline event
            timeline_event = OrderTimelineEvent(
                order_id=order_id,
                event_type="status_change",
                description=f"Order status changed from {OrderStatus.CLUSTER_QUEUED} to {OrderStatus.RUNNING}",
                event_metadata={"slurm_job_id": slurm_job_id, "cluster_name": cluster_name}
            )
            db.add(timeline_event)
            db.commit()

            logger.info("Production task completed (mock SLURM)", order_id=order_id)
            return {
                "status": "slurm_job_submitted",
                "slurm_job_id": slurm_job_id,
                "cluster_name": cluster_name,
                "cluster_info": {
                    "nodes": settings.SLURM_NUM_NODES,
                    "node_type": settings.SLURM_NODE_TYPE
                }
            }

    except Exception as e:
        logger.error("Production task failed", order_id=order_id, error=str(e))
        raise self.retry(countdown=300, max_retries=5, exc=e)

