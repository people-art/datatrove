"""
Payment service for Stripe integration
"""

import json
from typing import Any
from fastapi import Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.models.benchmark import OrderStatus
from app.services.order import OrderService
from app.services.benchmark import BenchmarkService
from app.services.slurm import SlurmProductionService
from app.core.config import settings

logger = structlog.get_logger(__name__)


class PaymentService:
    """Service for handling Stripe payments."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.order_service = OrderService(db)
        self.benchmark_service = BenchmarkService(db)
        self.slurm_service = SlurmProductionService(self.order_service)

    async def create_payment_intent(
        self,
        order_id: str,
        benchmark_job_id: str,
    ) -> str:
        """Create Stripe payment intent."""
        try:
            # Get quote for the benchmark job
            quote = await self.benchmark_service.calculate_quote(benchmark_job_id)

            # Create order
            order = await self.order_service.create_order(
                order_id=order_id,
                benchmark_job_id=benchmark_job_id,
                subtotal=quote["subtotal"],
                tax=quote["tax"],
                total=quote["total"],
                pricing_notes=quote["pricing_notes"],
                stripe_payment_intent_id=f"pi_{order_id}",  # Mock for development
                stripe_client_secret=f"pi_{order_id}_secret_{settings.SECRET_KEY[:10]}",  # Mock
            )

            # In production, this would create a real Stripe PaymentIntent
            # For now, we'll simulate it

            logger.info(
                "Payment intent created",
                order_id=order_id,
                amount=quote["total"]
            )

            return order.stripe_client_secret

        except Exception as e:
            logger.error(
                "Failed to create payment intent",
                order_id=order_id,
                benchmark_job_id=benchmark_job_id,
                error=str(e)
            )
            raise

    async def handle_webhook(self, request: Request) -> None:
        """Handle Stripe webhook events."""
        try:
            # In production, verify webhook signature
            # signature = request.headers.get("stripe-signature")
            # event = stripe.Webhook.construct_event(
            #     payload, signature, settings.STRIPE_WEBHOOK_SECRET
            # )

            # For development, we'll simulate webhook handling
            body = await request.body()
            event_data = json.loads(body.decode())

            event_type = event_data.get("type")
            payment_intent_id = event_data.get("data", {}).get("object", {}).get("id")

            if event_type == "payment_intent.succeeded":
                await self.handle_payment_success(payment_intent_id)
            elif event_type == "payment_intent.payment_failed":
                await self.handle_payment_failure(payment_intent_id)

            logger.info("Webhook processed", event_type=event_type)

        except Exception as e:
            logger.error("Webhook processing failed", error=str(e))
            raise HTTPException(status_code=400, detail="Webhook processing failed")

    async def handle_payment_success(self, payment_intent_id: str) -> None:
        """Handle successful payment."""
        # Find order by payment intent ID
        order = await self._get_order_by_payment_intent(payment_intent_id)
        if not order:
            logger.error("Order not found for payment intent", payment_intent_id=payment_intent_id)
            return

        # Update order status
        await self.order_service.update_order_status(
            order.id,
            OrderStatus.PAID
        )

        # Start production job
        await self.start_production_job(order.id, order.benchmark_job_id)

        logger.info("Payment succeeded", order_id=order.id)

    async def handle_payment_failure(self, payment_intent_id: str) -> None:
        """Handle failed payment."""
        order = await self._get_order_by_payment_intent(payment_intent_id)
        if not order:
            return

        await self.order_service.update_order_status(
            order.id,
            OrderStatus.FAILED,
            error_message="Payment failed"
        )

        logger.info("Payment failed", order_id=order.id)

    async def start_production_job(self, order_id: str, benchmark_job_id: str) -> None:
        """Start the full production job on Slurm."""
        # Update status to cluster queued
        await self.order_service.update_order_status(
            order_id,
            OrderStatus.CLUSTER_QUEUED
        )

        # TODO: Integrate with Slurm job submission
        # This would typically:
        # 1. Submit job to Slurm cluster
        # 2. Monitor job progress
        # 3. Upload results to Hugging Face
        # 4. Send email notification

        # For development, simulate the process
        await self._simulate_production_completion(order_id, benchmark_job_id)

    async def _simulate_production_completion(self, order_id: str, benchmark_job_id: str) -> None:
        """Simulate production completion for development."""
        import asyncio

        # Simulate processing time
        await asyncio.sleep(10)

        # Update status to running, then delivered
        await self.order_service.update_order_status(
            order_id,
            OrderStatus.RUNNING,
            fetched_docs=10000000,
            filtered_docs=8500000,
            deduped_docs=8000000,
            final_tokens=2000000000,  # 2B tokens
        )

        await asyncio.sleep(5)

        await self.order_service.update_order_status(
            order_id,
            OrderStatus.DELIVERED,
            hf_dataset_url=f"https://huggingface.co/datasets/finedata/{benchmark_job_id}",
            dataset_card_url=f"https://huggingface.co/datasets/finedata/{benchmark_job_id}/blob/main/README.md",
            invoice_url=f"https://api.finedata.com/invoices/{order_id}.pdf",
        )

        logger.info("Production job completed", order_id=order_id)

    async def _get_order_by_payment_intent(self, payment_intent_id: str):
        """Get order by Stripe payment intent ID."""
        # In production, this would query the database
        # For now, we'll extract order ID from the mock payment intent
        if payment_intent_id.startswith("pi_"):
            order_id = payment_intent_id.replace("pi_", "").split("_secret_")[0]
            return await self.order_service.get_order_by_id(order_id)
        return None
