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
