"""
Idempotency service for preventing duplicate operations
"""

import hashlib
import secrets
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
import structlog

from app.models.benchmark import IdempotencyKey
from app.core.errors import DuplicateResourceError

logger = structlog.get_logger(__name__)


class IdempotencyService:
    """Service for managing idempotency keys."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_idempotency_key(
        self,
        key: str,
        operation: str,
        user_id: Optional[str] = None,
        ttl_seconds: int = 86400  # 24 hours
    ) -> str:
        """Create or validate an idempotency key."""
        # Generate a hash of the key for consistent lookup
        key_hash = hashlib.sha256(key.encode()).hexdigest()

        # Check if key already exists
        stmt = select(IdempotencyKey).where(
            IdempotencyKey.key_hash == key_hash,
            IdempotencyKey.expires_at > datetime.utcnow()
        )
        result = await self.db.execute(stmt)
        existing_key = result.scalar_one_or_none()

        if existing_key:
            # Check if the operation is the same
            if existing_key.operation != operation:
                raise DuplicateResourceError(
                    "idempotency_key",
                    {"key": key, "existing_operation": existing_key.operation, "new_operation": operation}
                )

            # Return the existing response
            logger.info("Idempotency key found, returning cached response", key_hash=key_hash)
            return existing_key.response_data

        # Create new idempotency key
        idempotency_record = IdempotencyKey(
            key_hash=key_hash,
            operation=operation,
            user_id=user_id,
            expires_at=datetime.utcnow() + timedelta(seconds=ttl_seconds),
            response_data="{}",  # Placeholder, will be updated after operation
        )

        self.db.add(idempotency_record)
        await self.db.commit()

        logger.info("Idempotency key created", key_hash=key_hash, operation=operation)
        return ""  # Empty string indicates new operation

    async def update_idempotency_response(self, key_hash: str, response_data: str) -> None:
        """Update the response data for an idempotency key."""
        stmt = select(IdempotencyKey).where(IdempotencyKey.key_hash == key_hash)
        result = await self.db.execute(stmt)
        key_record = result.scalar_one_or_none()

        if key_record:
            key_record.response_data = response_data
            await self.db.commit()
            logger.info("Idempotency response updated", key_hash=key_hash)

    async def cleanup_expired_keys(self) -> int:
        """Clean up expired idempotency keys. Returns number of deleted keys."""
        stmt = delete(IdempotencyKey).where(IdempotencyKey.expires_at <= datetime.utcnow())
        result = await self.db.execute(stmt)
        deleted_count = result.rowcount
        await self.db.commit()

        if deleted_count > 0:
            logger.info("Cleaned up expired idempotency keys", count=deleted_count)

        return deleted_count


def get_idempotency_service(db_session):
    """Get an idempotency service instance."""
    return IdempotencyService(db_session)


def generate_idempotency_key(request_data: Dict[str, Any], user_id: Optional[str] = None) -> str:
    """Generate a deterministic idempotency key from request data."""
    # Create a stable representation of the request
    key_components = [
        str(user_id) if user_id else "anonymous",
        str(sorted(request_data.items()))  # Sort for consistency
    ]

    key_string = "|".join(key_components)
    return hashlib.sha256(key_string.encode()).hexdigest()


def generate_request_id() -> str:
    """Generate a unique request ID for tracing."""
    return secrets.token_hex(16)