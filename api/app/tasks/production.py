"""
Production task for full-scale dataset processing
"""

import asyncio
import uuid
import structlog
from app.worker import celery_app
from app.db.session import async_session_factory, session_factory
from app.models.benchmark import OrderStatus
from app.services.finewebdata_service import FineWebDataService, ProductionConfig
from app.core.config import settings

logger = structlog.get_logger(__name__)


@celery_app.task(bind=True, name="app.tasks.production_task")
def production_task(self, order_id: str):
    """
    Celery task to run full-scale dataset production with SLURM cluster.

    This task creates SLURM cluster and submits production job using finewebdata pipeline.
    """
    logger.info("Starting production task", order_id=order_id, task_id=self.request.id)

    try:
        # Use synchronous database operations for Celery compatibility
        from app.db.session import session_factory
        from app.models.benchmark import Order, OrderStatus, OrderTimelineEvent
        from app.services.slurm import SlurmProductionService
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        # Use sync database session
        with session_factory() as db:
            # Get order details with joined benchmark job
            stmt = select(Order).options(selectinload(Order.benchmark_job)).where(Order.id == order_id)
            result = db.execute(stmt)
            order = result.scalar_one_or_none()

            if not order or not order.benchmark_job:
                raise Exception(f"Order or benchmark job not found: {order_id}")

            benchmark_job = order.benchmark_job

            # Check if mock production mode is enabled
            if settings.FINEDATA_MOCK_PRODUCTION:
                logger.info("Mock production mode enabled, simulating production process", order_id=order_id)

                # Simulate production by updating order status to running, then completed
                from app.services.order import OrderService
                order_service = OrderService(db)

                # Update to running status
                order_service.update_order_status_sync(db, order_id, OrderStatus.RUNNING, "Mock production running")

                # Simulate processing time
                import time
                time.sleep(5)  # Simulate 5 seconds of processing

                # Update to completed status with mock data
                mock_hf_url = f"https://huggingface.co/datasets/finedata/{order_id}"
                mock_dataset_card = f"https://huggingface.co/datasets/finedata/{order_id}/README.md"

                # Update order status to delivered
            # Create production config
            production_config = ProductionConfig(
                order_id=order_id,
                benchmark_job_id=benchmark_job.id,
                domain=benchmark_job.domain,
                keywords=benchmark_job.keywords,
                languages=benchmark_job.languages,
                time_range_start=benchmark_job.time_range_start,
                time_range_end=benchmark_job.time_range_end,
                quality_tier=benchmark_job.quality_tier,
            )

            # Initialize SLURM production service
            from app.services.order import OrderService
            order_service = OrderService(db)
            slurm_service = SlurmProductionService(order_service)

            # Start production job - this creates cluster and submits job
            slurm_job_id = slurm_service.start_production_job_sync(
                db,
                order_id=order_id,
                benchmark_job_id=benchmark_job.id,
                domain=benchmark_job.domain,
                keywords=benchmark_job.keywords,
                languages=benchmark_job.languages,
                time_range_start=benchmark_job.time_range_start,
                time_range_end=benchmark_job.time_range_end,
                quality_tier=benchmark_job.quality_tier,
            )

            # Start monitoring task
            production_monitor_task.delay(order_id, slurm_job_id)

            logger.info("Production task completed - SLURM job submitted", order_id=order_id, slurm_job_id=slurm_job_id)
            return {
                "status": "slurm_job_submitted",
                "slurm_job_id": slurm_job_id,
                "cluster_name": slurm_service.cluster_manager.cluster_name,
                "cluster_info": {
                    "nodes": settings.SLURM_NUM_NODES,
                    "node_type": settings.SLURM_NODE_TYPE
                }
            }

    except Exception as e:
        logger.error("Production task failed", order_id=order_id, error=str(e))

        # Update order status to failed
        try:
            from app.db.session import session_factory
            from app.models.benchmark import Order, OrderStatus, OrderTimelineEvent

            with session_factory() as db:
                order = db.query(Order).filter(Order.id == order_id).first()
                if order:
                    order.status = OrderStatus.FAILED
                    order.error_message = str(e)
                    db.commit()

                    # Add failure timeline event
                    timeline_event = OrderTimelineEvent(
                        order_id=order_id,
                        event_type="error",
                        description=f"Production failed: {str(e)}",
                        event_metadata={"error": str(e)}
                    )
                    db.add(timeline_event)
                    db.commit()

        except Exception as db_error:
            logger.error("Failed to update order status on failure", order_id=order_id, error=str(db_error))

        raise self.retry(countdown=300, max_retries=5, exc=e)


@celery_app.task(bind=True, name="app.tasks.production_monitor")
def production_monitor_task(self, order_id: str, slurm_job_id: str):
    """
    Monitor production SLURM job status and handle completion.

    This task periodically checks SLURM job status and triggers delivery
    when the job completes successfully.
    """
    logger.info("Starting production monitor", order_id=order_id, slurm_job_id=slurm_job_id)

    try:
        from app.db.session import session_factory
        from app.models.benchmark import Order, OrderStatus, OrderTimelineEvent
        from app.services.slurm import SlurmProductionService
        from app.services.finewebdata_service import FineWebDataService

        with session_factory() as db:
            # Get order details
            order = db.query(Order).filter(Order.id == order_id).first()
            if not order:
                logger.error("Order not found for monitoring", order_id=order_id)
                return

            # Check SLURM job status
            slurm_service = SlurmProductionService(None)  # We don't need order service for monitoring
            job_status = slurm_service.check_job_status_sync(slurm_job_id)

            current_status = job_status.get('status', 'UNKNOWN')
            logger.info("SLURM job status check", order_id=order_id, slurm_job_id=slurm_job_id, status=current_status)

            if current_status in ['COMPLETED', 'DONE']:
                # Job completed successfully - trigger delivery
                logger.info("SLURM job completed, triggering delivery", order_id=order_id)

                # Update order status to finalizing
                order.status = OrderStatus.FINALIZING
                db.commit()

                # Add timeline event
                timeline_event = OrderTimelineEvent(
                    order_id=order_id,
                    event_type="status_change",
                    description=f"Order status changed from {OrderStatus.RUNNING} to {OrderStatus.FINALIZING}",
                    event_metadata={"slurm_job_id": slurm_job_id, "completion_status": current_status}
                )
                db.add(timeline_event)
                db.commit()

                # Trigger HuggingFace upload
                try:
                    benchmark_job = order.benchmark_job
                    if benchmark_job:
                        hf_service = FineWebDataService()
                        hf_url = hf_service.upload_to_huggingface_sync(order_id, benchmark_job.domain)

                        # Update order with delivery URLs
                        order.hf_dataset_url = hf_url
                        order.dataset_card_url = f"{hf_url}#dataset-card"
                        order.status = OrderStatus.DELIVERED
                        db.commit()

                        # Add delivery timeline event
                        delivery_event = OrderTimelineEvent(
                            order_id=order_id,
                            event_type="delivery",
                            description="Dataset delivered to HuggingFace",
                            event_metadata={"hf_url": hf_url}
                        )
                        db.add(delivery_event)
                        db.commit()

                        logger.info("Production delivery completed", order_id=order_id, hf_url=hf_url)

                        # Cleanup SLURM cluster
                        if hasattr(slurm_service, 'cluster_manager') and slurm_service.cluster_manager:
                            slurm_service.cluster_manager.delete_cluster_sync()

                    else:
                        raise Exception("Benchmark job not found for delivery")

                except Exception as delivery_error:
                    logger.error("Delivery failed", order_id=order_id, error=str(delivery_error))

                    # Update order status to failed
                    order.status = OrderStatus.FAILED
                    order.error_message = f"Delivery failed: {str(delivery_error)}"
                    db.commit()

                    # Add failure timeline event
                    failure_event = OrderTimelineEvent(
                        order_id=order_id,
                        event_type="error",
                        description=f"Delivery failed: {str(delivery_error)}",
                        event_metadata={"error": str(delivery_error)}
                    )
                    db.add(failure_event)
                    db.commit()

            elif current_status in ['FAILED', 'CANCELLED', 'TIMEOUT']:
                # Job failed
                logger.error("SLURM job failed", order_id=order_id, slurm_job_id=slurm_job_id, status=current_status)

                # Update order status to failed
                order.status = OrderStatus.FAILED
                order.error_message = f"SLURM job {current_status}: {job_status.get('reason', 'Unknown error')}"
                db.commit()

                # Add failure timeline event
                failure_event = OrderTimelineEvent(
                    order_id=order_id,
                    event_type="error",
                    description=f"SLURM job failed: {current_status}",
                    event_metadata={"slurm_job_id": slurm_job_id, "status": current_status}
                )
                db.add(failure_event)
                db.commit()

                # Cleanup cluster on failure
                if hasattr(slurm_service, 'cluster_manager') and slurm_service.cluster_manager:
                    slurm_service.cluster_manager.delete_cluster_sync()

            else:
                # Job still running - schedule next check
                logger.info("SLURM job still running, scheduling next check", order_id=order_id, status=current_status)
                # Re-queue this monitoring task in 5 minutes
                production_monitor_task.apply_async(
                    args=[order_id, slurm_job_id],
                    countdown=300  # 5 minutes
                )

    except Exception as e:
        logger.error("Production monitor task failed", order_id=order_id, slurm_job_id=slurm_job_id, error=str(e))
        # Re-queue monitoring with longer delay on error
        production_monitor_task.apply_async(
            args=[order_id, slurm_job_id],
            countdown=600  # 10 minutes
        )

