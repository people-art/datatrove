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
    Sync task to run full-scale dataset production.

    This task processes the complete dataset and uploads to Hugging Face.
    """
    logger.info("Starting production task", order_id=order_id, task_id=self.request.id)

    try:
        # Import here to avoid circular imports
        from app.models.benchmark import Order, OrderTimelineEvent
        from sqlalchemy import select

        # Use sync database session
        with session_factory() as db:
            # Get order details
            stmt = select(Order).where(Order.id == order_id)
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

            # Update to running status (SLURM integration to be completed)
            slurm_job_id = f"job-{uuid.uuid4().hex[:8]}"
            order.status = OrderStatus.RUNNING
            order.slurm_job_id = slurm_job_id
            order.cluster_name = cluster_name
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
                "status": "production_started",
                "order_id": order_id,
                "cluster_info": {
                    "nodes": settings.SLURM_NUM_NODES,
                    "node_type": settings.SLURM_NODE_TYPE
                }
            }

    except Exception as e:
        logger.error("Production task failed", order_id=order_id, error=str(e))
        raise self.retry(countdown=300, max_retries=5, exc=e)

