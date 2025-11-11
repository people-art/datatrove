"""
Order management API endpoints
"""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.schemas import benchmark as schemas
from app.db.dependencies import get_db
from app.services.order import OrderService
from app.services.payment import PaymentService
from app.services.idempotency import IdempotencyService, generate_idempotency_key
from app.core.errors import DuplicateResourceError, handle_business_error

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.post("", response_model=schemas.OrderCreateResponse)
async def create_order(
    data: schemas.OrderCreateRequest,
    idempotency_key: str = None,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Create a new order for dataset generation.

    Uses idempotency to prevent duplicate orders.
    """
    try:
        idempotency_service = IdempotencyService(db)
        order_service = OrderService(db)

        # Generate idempotency key if not provided
        if not idempotency_key:
            key_data = {
                "quote_id": data.quoteId,
                "job_id": data.jobId,
                "email": data.email
            }
            idempotency_key = generate_idempotency_key(key_data)

        # Check for existing operation
        cached_response = await idempotency_service.create_idempotency_key(
            key=idempotency_key,
            operation="create_order",
            user_id=data.email,  # Use email as user identifier
            ttl_seconds=3600  # 1 hour
        )

        if cached_response:
            # Return cached response for duplicate request
            import json
            cached_data = json.loads(cached_response)
            logger.info("Returning cached order response", order_id=cached_data["orderId"])
            return schemas.OrderCreateResponse(**cached_data)

        # Create order with quote and benchmark job binding
        order_data = await order_service.create_order(
            quote_id=data.quoteId,
            job_id=data.jobId,
            email=data.email
        )

        # Cache the response
        response_data = {
            "orderId": order_data["id"],
            "provider": "stripe",
            "clientSecret": order_data["client_secret"]
        }
        await idempotency_service.update_idempotency_response(
            key_hash=idempotency_key,
            response_data=json.dumps(response_data)
        )

        logger.info("Order created", order_id=order_data["id"], quote_id=data.quoteId)

        return schemas.OrderCreateResponse(**response_data)

    except DuplicateResourceError as e:
        logger.warning("Duplicate order creation attempt", error=e.details)
        raise handle_business_error(e)
    except Exception as e:
        logger.error("Failed to create order", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create order")


@router.get("/{order_id}/production", response_model=schemas.ProductionStatusResponse)
async def get_production_status(
    order_id: str,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get production task status for an order.
    """
    try:
        order_service = OrderService(db)
        production_status = await order_service.get_production_status(order_id)

        if not production_status:
            raise HTTPException(status_code=404, detail="Production status not found")

        return schemas.ProductionStatusResponse(**production_status)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get production status", order_id=order_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get production status")


@router.get("/{order_id}", response_model=schemas.OrderResponse)
async def get_order(
    order_id: str,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get order status and details.
    """
    try:
        order_service = OrderService(db)
        order_data = await order_service.get_order(order_id)

        if not order_data:
            raise HTTPException(status_code=404, detail="Order not found")

        return schemas.OrderResponse(**order_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get order", order_id=order_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get order")


@router.post("/{order_id}/mock-payment", response_model=schemas.OrderResponse)
async def mock_payment_and_start_production(
    order_id: str,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Mock payment success and start production job.

    This endpoint simulates payment completion and immediately starts the
    SLURM production job for development/testing purposes.
    """
    try:
        payment_service = PaymentService(db)

        # Mock payment success and start production
        await payment_service.mock_payment_success(order_id)

        # Return updated order status
        order_service = OrderService(db)
        order_data = await order_service.get_order(order_id)

        if not order_data:
            raise HTTPException(status_code=404, detail="Order not found")

        logger.info("Mock payment completed and production started", order_id=order_id)
        return schemas.OrderResponse(**order_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to mock payment and start production", order_id=order_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to mock payment and start production")
