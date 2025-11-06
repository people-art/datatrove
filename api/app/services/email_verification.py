"""
Email verification service
"""

import uuid
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import structlog
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models.email_verification import EmailVerification
from app.services.email import get_email_service
from app.core.errors import AppError, ErrorCode, ValidationError

logger = structlog.get_logger(__name__)


class EmailVerificationService:
    """Service for managing email verification"""

    def __init__(self):
        self.email_service = get_email_service()
        self.token_expiry_hours = 24  # 24 hours

    async def create_verification(
        self,
        db: AsyncSession,
        email: str,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> str:
        """Create a new email verification token"""

        # Validate email format
        if not self._is_valid_email(email):
            raise ValidationError("email", email, "Invalid email format")

        # Generate token
        token = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(hours=self.token_expiry_hours)

        # Check if email is already verified
        existing = await self._get_verification_by_email(db, email)
        if existing and existing.is_verified:
            logger.info("Email already verified", email=email)
            return token  # Return token anyway for consistency

        # Create or update verification record
        if existing:
            # Update existing record
            await db.execute(
                update(EmailVerification).where(EmailVerification.email == email).values(
                    token=token,
                    expires_at=expires_at,
                    is_verified=False,
                    verified_at=None,
                    verification_attempts="[]",
                    user_agent=user_agent,
                    ip_address=ip_address
                )
            )
        else:
            # Create new record
            verification = EmailVerification(
                id=str(uuid.uuid4()),
                email=email,
                token=token,
                expires_at=expires_at,
                user_agent=user_agent,
                ip_address=ip_address
            )
            db.add(verification)

        await db.commit()

        # Send verification email
        try:
            self.email_service.send_verification_email(email, token)
            logger.info("Verification email sent", email=email, token=token)
        except Exception as e:
            logger.error("Failed to send verification email", email=email, error=str(e))
            # Don't fail the request if email sending fails

        return token

    async def verify_email(
        self,
        db: AsyncSession,
        token: str,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """Verify an email using token"""

        # Find verification record
        result = await db.execute(
            select(EmailVerification).where(EmailVerification.token == token)
        )
        verification = result.scalar_one_or_none()

        if not verification:
            raise AppError(
                "Invalid verification token",
                ErrorCode.VALIDATION_ERROR,
                user_message="This verification link is invalid or has expired."
            )

        # Check if already verified
        if verification.is_verified:
            return {
                "email": verification.email,
                "verified": True,
                "message": "Email was already verified"
            }

        # Check if expired
        if datetime.utcnow() > verification.expires_at:
            raise AppError(
                "Verification token expired",
                ErrorCode.VALIDATION_ERROR,
                user_message="This verification link has expired. Please request a new one."
            )

        # Check rate limiting (max 5 attempts per hour)
        attempts = json.loads(verification.verification_attempts or "[]")
        recent_attempts = [
            datetime.fromisoformat(ts) for ts in attempts
            if datetime.utcnow() - datetime.fromisoformat(ts) < timedelta(hours=1)
        ]

        if len(recent_attempts) >= 5:
            raise AppError(
                "Too many verification attempts",
                ErrorCode.VALIDATION_ERROR,
                user_message="Too many verification attempts. Please wait and try again."
            )

        # Record this attempt
        attempts.append(datetime.utcnow().isoformat())
        verification.verification_attempts = json.dumps(attempts[-10:])  # Keep last 10 attempts

        # Mark as verified
        verification.is_verified = True
        verification.verified_at = datetime.utcnow()
        verification.user_agent = user_agent or verification.user_agent
        verification.ip_address = ip_address or verification.ip_address

        await db.commit()

        logger.info("Email verified successfully", email=verification.email, token=token)

        return {
            "email": verification.email,
            "verified": True,
            "message": "Email verified successfully"
        }

    async def is_email_verified(self, db: AsyncSession, email: str) -> bool:
        """Check if an email is verified"""
        verification = await self._get_verification_by_email(db, email)
        return verification.is_verified if verification else False

    async def resend_verification(
        self,
        db: AsyncSession,
        email: str,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> str:
        """Resend verification email"""
        return await self.create_verification(db, email, user_agent, ip_address)

    async def _get_verification_by_email(self, db: AsyncSession, email: str) -> Optional[EmailVerification]:
        """Get verification record by email"""
        result = await db.execute(
            select(EmailVerification).where(EmailVerification.email == email)
        )
        return result.scalar_one_or_none()

    def _is_valid_email(self, email: str) -> bool:
        """Basic email validation"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))


# Global instance
email_verification_service = EmailVerificationService()


def get_email_verification_service() -> EmailVerificationService:
    """Dependency injection for email verification service"""
    return email_verification_service
