"""
Payment API endpoints
"""

import uuid
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.schemas import benchmark as schemas
from app.db.dependencies import get_db
from app.services.payment import PaymentService
from app.core.config import settings

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.post("/session", response_model=schemas.CheckoutSessionResponse)
async def create_checkout_session(
    request: schemas.CheckoutSessionRequest,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Create Stripe checkout session for payment.
    """
    try:
        payment_service = PaymentService(db)

        # Create order and payment intent
        order_id = str(uuid.uuid4())
        client_secret = await payment_service.create_payment_intent(
            order_id=order_id,
            benchmark_job_id=request.jobId,
        )

        logger.info(
            "Checkout session created",
            order_id=order_id,
            benchmark_job_id=request.jobId
        )

        return schemas.CheckoutSessionResponse(
            client_secret=client_secret,
            orderId=order_id
        )

    except Exception as e:
        logger.error(
            "Failed to create checkout session",
            benchmark_job_id=request.jobId,
            error=str(e)
        )
        raise HTTPException(status_code=500, detail="Failed to create checkout session")


@router.post("/webhooks")
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Handle Stripe webhooks for payment events.
    """
    try:
        payment_service = PaymentService(db)
        await payment_service.handle_webhook(request)

        return {"status": "ok"}

    except Exception as e:
        logger.error("Webhook processing failed", error=str(e))
        raise HTTPException(status_code=400, detail="Webhook processing failed")


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Handle Stripe webhook events for payment completion.
    """
    try:
        payment_service = PaymentService(db)

        # Get raw body for signature verification
        body = await request.body()
        signature = request.headers.get("stripe-signature")

        # Process webhook
        event = await payment_service.process_webhook(body, signature)

        logger.info("Webhook processed", event_type=event.get("type"))

        return {"status": "ok"}

    except Exception as e:
        logger.error("Webhook processing failed", error=str(e))
        raise HTTPException(status_code=400, detail="Webhook processing failed")
