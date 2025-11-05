"""
Main API router for v1 endpoints
"""

from fastapi import APIRouter

from app.api.api_v1.endpoints import benchmark, orders, payments

api_router = APIRouter()

api_router.include_router(
    benchmark.router,
    prefix="/benchmark",
    tags=["benchmark"]
)

api_router.include_router(
    orders.router,
    prefix="/orders",
    tags=["orders"]
)

api_router.include_router(
    payments.router,
    prefix="/checkout",
    tags=["payments"]
)
