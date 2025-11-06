"""
Idempotency middleware for FastAPI
"""

import json
from typing import Optional
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
import structlog

from app.services.idempotency import get_idempotency_service

logger = structlog.get_logger(__name__)

IDEMPOTENCY_HEADER = "X-Idempotency-Key"
IDEMPOTENCY_ENDPOINTS = {
    "POST": [
        "/api/v1/benchmark/quote",
        "/api/v1/benchmark/jobs",
        "/api/v1/orders",
        "/api/v1/payments/session"
    ]
}


class IdempotencyMiddleware:
    """Middleware to handle request idempotency"""

    def __init__(self, app):
        self.app = app
        self.idempotency_service = None  # Will be created per request

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)

        # Check if this endpoint requires idempotency
        method = request.method
        path = request.url.path

        requires_idempotency = (
            method in IDEMPOTENCY_ENDPOINTS and
            any(path.startswith(endpoint) for endpoint in IDEMPOTENCY_ENDPOINTS[method])
        )

        if not requires_idempotency:
            await self.app(scope, receive, send)
            return

        # Extract idempotency key
        idempotency_key = request.headers.get(IDEMPOTENCY_HEADER)
        if not idempotency_key:
            # For required endpoints, generate a key based on request content
            # This is a fallback - clients should provide explicit keys
            body = await self._read_body(request)
            idempotency_key = self._generate_fallback_key(method, path, body)
            logger.warning(
                "Missing idempotency key, using fallback",
                method=method,
                path=path,
                fallback_key=idempotency_key
            )

        # Check for duplicate request
        try:
            body_dict = json.loads(body) if body else None
        except (json.JSONDecodeError, TypeError):
            body_dict = None

        is_duplicate, previous_response = self.idempotency_service.check_and_store(
            idempotency_key=idempotency_key,
            method=method,
            url=str(request.url),
            body=body_dict
        )

        if is_duplicate and previous_response:
            logger.info(
                "Returning cached response for duplicate request",
                idempotency_key=idempotency_key,
                status_code=previous_response.get("status_code", 200)
            )

            # Create response from cached data
            response = JSONResponse(
                status_code=previous_response.get("status_code", 200),
                content=previous_response.get("content", {})
            )

            await response(scope, receive, send)
            return

        # Process the request normally
        await self.app(scope, receive, send)

    async def _read_body(self, request: Request) -> Optional[str]:
        """Read request body safely"""
        try:
            body_bytes = await request.body()
            return body_bytes.decode("utf-8") if body_bytes else None
        except Exception:
            return None

    def _generate_fallback_key(self, method: str, path: str, body: Optional[str]) -> str:
        """Generate a fallback idempotency key"""
        import hashlib
        import time

        key_data = f"{method}:{path}:{body or ''}:{int(time.time() // 300)}"  # 5-minute windows
        return hashlib.md5(key_data.encode()).hexdigest()


async def idempotency_response_middleware(request: Request, call_next):
    """Middleware to store responses for idempotency"""
    response = await call_next(request)

    # Check if this was an idempotent request
    idempotency_key = request.headers.get(IDEMPOTENCY_HEADER)
    if not idempotency_key:
        return response

    method = request.method
    path = request.url.path

    requires_idempotency = (
        method in IDEMPOTENCY_ENDPOINTS and
        any(path.startswith(endpoint) for endpoint in IDEMPOTENCY_ENDPOINTS[method])
    )

    if not requires_idempotency:
        return response

    # Store the response
    try:
        if hasattr(response, 'body'):
            # For responses with body
            content = response.body.decode() if isinstance(response.body, bytes) else str(response.body)
            try:
                content_dict = json.loads(content)
            except (json.JSONDecodeError, TypeError):
                content_dict = {"content": content}

            stored_response = {
                "status_code": response.status_code,
                "content": content_dict
            }

            # Generate request hash for storage
            body = await request.body()
            try:
                body_dict = json.loads(body.decode()) if body else None
            except (json.JSONDecodeError, TypeError):
                body_dict = None

            import hashlib
            request_hash = hashlib.sha256(
                json.dumps({
                    "method": method,
                    "url": str(request.url),
                    "body": body_dict or {}
                }, sort_keys=True).encode()
            ).hexdigest()

            idempotency_service = get_idempotency_service()
            idempotency_service.store_response(idempotency_key, request_hash, stored_response)

    except Exception as e:
        logger.warning("Failed to store response for idempotency", error=str(e))

    return response
