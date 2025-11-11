"""
Order service for managing orders
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

from app.models.benchmark import Order, OrderStatus, OrderTimelineEvent
from app.schemas.benchmark import OrderTimelineEvent as TimelineEventSchema

logger = structlog.get_logger(__name__)


class OrderService:
    """Service for managing orders."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_order(
        self,
        order_id: str,
        benchmark_job_id: str,
        subtotal: float,
        tax: float,
        total: float,
        pricing_notes: str,
        stripe_payment_intent_id: str,
        stripe_client_secret: str,
    ) -> Order:
        """Create a new order."""
        order = Order(
            id=order_id,
            benchmark_job_id=benchmark_job_id,
            status=OrderStatus.AWAITING_PAYMENT,
            currency="USD",
            subtotal=subtotal,
            tax=tax,
            total=total,
            pricing_notes=pricing_notes,
            stripe_payment_intent_id=stripe_payment_intent_id,
            stripe_client_secret=stripe_client_secret,
        )

        self.db.add(order)
        await self.db.commit()
        await self.db.refresh(order)

        # Add timeline event
        await self.add_timeline_event(
            order_id,
            "Order created",
            f"Order created for benchmark job {benchmark_job_id}",
            None
        )

        return order

    async def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get order with timeline."""
        stmt = select(Order).where(Order.id == order_id)
        result = await self.db.execute(stmt)
        order = result.scalar_one_or_none()

        if not order:
            return None

        # Get timeline events
        stmt = select(OrderTimelineEvent).where(OrderTimelineEvent.order_id == order_id)
        result = await self.db.execute(stmt)
        timeline_events = result.scalars().all()

        timeline = [
            TimelineEventSchema(
                timestamp=event.timestamp.isoformat(),
                label=event.description
            )
            for event in timeline_events
        ]

        # Live stats (when running)
        live_stats = None
        if order.status in [OrderStatus.RUNNING, OrderStatus.CLUSTER_QUEUED]:
            live_stats = {
                "fetched": order.fetched_docs,
                "filtered": order.filtered_docs,
                "deduped": order.deduped_docs,
                "tokens": order.final_tokens,
            }

        # Delivery info (when delivered)
        delivery_info = None
        if order.status == OrderStatus.DELIVERED:
            delivery_info = {
                "hf_url": order.hf_dataset_url,
                "dataset_card": order.dataset_card_url,
                "invoice_url": order.invoice_url,
            }

        return {
            "id": order.id,
            "status": order.status.value,
            "timeline": timeline,
            "live": live_stats,
            "delivery": delivery_info,
            "error": order.error_message,
        }

    async def update_order_status(
        self,
        order_id: str,
        status: OrderStatus,
        error_message: Optional[str] = None,
        **kwargs
    ) -> None:
        """Update order status."""
        order = await self.get_order_by_id(order_id)
        if not order:
            return

        old_status = order.status
        order.status = status

        if error_message:
            order.error_message = error_message

        # Update other fields
        for key, value in kwargs.items():
            if hasattr(order, key):
                setattr(order, key, value)

        await self.db.commit()

        # Add timeline event for status change
        if old_status != status:
            await self.add_timeline_event(
                order_id,
                f"Status changed to {status.value}",
                f"Order status changed from {old_status.value} to {status.value}",
                None
            )

    async def get_order_by_id(self, order_id: str) -> Optional[Order]:
        """Get order by ID."""
        stmt = select(Order).where(Order.id == order_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def add_timeline_event(
        self,
        order_id: str,
        event_type: str,
        description: str,
        event_metadata: Optional[Dict] = None
    ) -> None:
        """Add timeline event to order."""
        event = OrderTimelineEvent(
            order_id=order_id,
            event_type=event_type,
            description=description,
            event_metadata=event_metadata or {},
        )

        self.db.add(event)
        await self.db.commit()

    async def create_order(
        self,
        quote_id: str,
        job_id: str,
        email: str
    ) -> Dict[str, Any]:
        """Create a new order bound to a quote and benchmark job."""
        # Create payment intent via PaymentService
        # Import here to avoid circular import
        from app.services.payment import PaymentService
        payment_service = PaymentService(self.db)
        payment_intent = await payment_service.create_payment_intent_for_quote(quote_id)

        # Create order record
        # Extract suffix from quote_id, handle different formats gracefully
        if '_' in quote_id:
            order_suffix = quote_id.split('_')[1]
        else:
            # Fallback for non-standard quote_id formats
            order_suffix = quote_id.replace('q_', '').replace('quote_', '')[:16]

        order_id = f"order_{order_suffix}"

        # For now, create a placeholder order - in production this would be more sophisticated
        order = Order(
            id=order_id,
            benchmark_job_id=job_id,
            status=OrderStatus.AWAITING_PAYMENT,
            currency="USD",
            subtotal=100.0,  # Placeholder - would come from quote
            tax=8.0,        # Placeholder - would come from quote
            total=108.0,    # Placeholder - would come from quote
            pricing_notes="Quote-based pricing",
            stripe_payment_intent_id=payment_intent.id,
            stripe_client_secret=payment_intent.client_secret,
            quote_id=quote_id,
            email=email
        )

        self.db.add(order)
        await self.db.commit()
        await self.db.refresh(order)

        # Add timeline event
        await self.add_timeline_event(
            order_id,
            "order_created",
            f"Order created for quote {quote_id} and job {job_id}",
            {"quote_id": quote_id, "job_id": job_id, "email": email}
        )

        return {
            "id": order_id,
            "client_secret": payment_intent.client_secret
        }

    async def get_production_status(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get production task status for an order."""
        stmt = select(Order).where(Order.id == order_id)
        result = await self.db.execute(stmt)
        order = result.scalar_one_or_none()

        if not order:
            return None

        # Map order status to production status
        status_mapping = {
            OrderStatus.CLUSTER_QUEUED: "initializing",
            OrderStatus.RUNNING: "running",
            OrderStatus.FINALIZING: "publishing",
            OrderStatus.DELIVERED: "delivered",
            OrderStatus.FAILED: "failed"
        }

        production_status = status_mapping.get(order.status, "unknown")

        return {
            "status": production_status,
            "estCompleteAt": None,  # Would be calculated based on job progress
            "logsUrl": None,       # Would point to Slurm logs
            "error": order.error_message if order.status == OrderStatus.FAILED else None
        }
