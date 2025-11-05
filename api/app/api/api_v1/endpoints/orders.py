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

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.post("", response_model=schemas.OrderCreateResponse)
async def create_order(
    data: schemas.OrderCreateRequest,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Create a new order for dataset generation.
    """
    try:
        order_service = OrderService(db)

        # Create order with quote and benchmark job binding
        order_data = await order_service.create_order(
            quote_id=data.quoteId,
            job_id=data.jobId,
            email=data.email
        )

        logger.info("Order created", order_id=order_data["id"], quote_id=data.quoteId)

        return schemas.OrderCreateResponse(
            orderId=order_data["id"],
            provider="stripe",  # For now, only Stripe is supported
            clientSecret=order_data["client_secret"]
        )

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
