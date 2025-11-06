"""
Email verification models
"""

from sqlalchemy import Column, String, DateTime, Boolean, Text
from sqlalchemy.sql import func

from app.db.base import Base


class EmailVerification(Base):
    """Email verification tokens"""

    __tablename__ = "email_verifications"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, nullable=False, index=True)
    token = Column(String, nullable=False, unique=True, index=True)
    is_verified = Column(Boolean, default=False, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    verified_at = Column(DateTime(timezone=True), nullable=True)
    verification_attempts = Column(String, default=0, nullable=False)  # JSON array of timestamps

    # Metadata
    user_agent = Column(Text, nullable=True)
    ip_address = Column(String, nullable=True)
