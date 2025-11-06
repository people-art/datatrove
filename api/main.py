"""
FineData API - Custom Domain Dataset Generation Service
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import structlog

from app.api.api_v1.api import api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.error_handlers import setup_error_handlers
# from app.middleware.idempotency import IdempotencyMiddleware, idempotency_response_middleware
from app.db.session import engine
from app.db.base import Base

# Setup structured logging
setup_logging()
logger = structlog.get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    Handles startup and shutdown events.
    """
    logger.info("Starting FineData API")

    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Database tables created/verified")

    yield

    logger.info("Shutting down FineData API")

def create_application() -> FastAPI:
    """
    Create and configure FastAPI application.
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="API for generating custom domain-specific datasets",
        version="1.0.0",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Set up CORS
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Add trusted host middleware
    if not settings.DEBUG:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.ALLOWED_HOSTS,
        )

    # Add idempotency middleware
    # app.add_middleware(IdempotencyMiddleware)

    # Include API router
    app.include_router(api_router, prefix=settings.API_V1_STR)

    # Setup error handlers
    setup_error_handlers(app)

    # Add idempotency response middleware (disabled for now)
    # TODO: Implement proper idempotency middleware
    # app.middleware("http")(idempotency_response_middleware)

    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "version": "1.0.0"}

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """Log all HTTP requests."""
        logger.info(
            "HTTP Request",
            method=request.method,
            url=str(request.url),
            client_ip=request.client.host,
        )
        response = await call_next(request)
        logger.info(
            "HTTP Response",
            status_code=response.status_code,
            method=request.method,
            url=str(request.url),
        )
        return response

    return app

app = create_application()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_config=None,  # Use our custom logging
    )
