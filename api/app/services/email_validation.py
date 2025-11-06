"""
Email validation service for verifying email addresses
"""

import re
import dns.resolver
import dns.exception
import smtplib
import socket
from datetime import datetime
from typing import Dict, Optional, Tuple
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import structlog

from app.core.config import settings
from app.core.errors import ValidationError, BusinessError

logger = structlog.get_logger(__name__)


class EmailValidationService:
    """Service for validating and verifying email addresses."""

    def __init__(self):
        self.smtp_timeout = 10  # seconds

    def validate_format(self, email: str) -> bool:
        """Validate basic email format using regex."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def extract_domain(self, email: str) -> str:
        """Extract domain from email address."""
        try:
            return email.split('@')[1].lower()
        except IndexError:
            raise ValidationError("Invalid email format")

    async def validate_mx_records(self, domain: str) -> bool:
        """Check if domain has valid MX records."""
        try:
            # Query MX records for the domain
            answers = dns.resolver.resolve(domain, 'MX')
            return len(answers) > 0
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.exception.Timeout):
            logger.warning("MX record check failed", domain=domain)
            return False
        except Exception as e:
            logger.error("MX record check error", domain=domain, error=str(e))
            return False

    def validate_smtp_connection(self, domain: str) -> bool:
        """Test SMTP connection to domain (basic check)."""
        try:
            # Get MX records
            answers = dns.resolver.resolve(domain, 'MX')
            if not answers:
                return False

            # Get the highest priority MX server
            mx_server = str(sorted(answers, key=lambda x: x.preference)[0].exchange).rstrip('.')

            # Try to connect to SMTP server
            server = smtplib.SMTP(mx_server, timeout=self.smtp_timeout)
            server.quit()
            return True

        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.exception.Timeout,
                smtplib.SMTPException, socket.error):
            return False
        except Exception as e:
            logger.error("SMTP validation error", domain=domain, error=str(e))
            return False

    async def validate_email(self, email: str) -> Dict[str, any]:
        """Comprehensive email validation."""
        email = email.strip().lower()

        # Format validation
        if not self.validate_format(email):
            raise ValidationError("Invalid email format")

        domain = self.extract_domain(email)

        # Check for disposable/temporary email domains
        if await self.is_disposable_domain(domain):
            raise BusinessError(
                code="EMAIL_DISPOSABLE",
                message="Disposable email addresses not allowed",
                details="Please use a permanent email address"
            )

        # MX record validation
        if not await self.validate_mx_records(domain):
            raise ValidationError("Invalid domain - no mail servers found")

        # Basic SMTP validation (optional, can be slow)
        smtp_valid = self.validate_smtp_connection(domain)
        if not smtp_valid:
            logger.warning("SMTP connection failed, but allowing email", email=email, domain=domain)

        return {
            "email": email,
            "domain": domain,
            "format_valid": True,
            "mx_valid": True,
            "smtp_valid": smtp_valid,
            "is_disposable": False
        }

    async def is_disposable_domain(self, domain: str) -> bool:
        """Check if domain is known to be disposable/temporary."""
        # Common disposable email domains
        disposable_domains = {
            '10minutemail.com', 'guerrillamail.com', 'mailinator.com',
            'temp-mail.org', 'throwaway.email', 'yopmail.com',
            'maildrop.cc', 'tempail.com', 'getnada.com', 'mail.tm'
        }

        return domain in disposable_domains

    async def send_verification_email(self, email: str, verification_token: str) -> bool:
        """Send email verification link."""
        try:
            # This would integrate with your email service (SendGrid, etc.)
            # For now, just log the verification request
            logger.info("Email verification requested",
                       email=email,
                       token=verification_token[:8] + "...")

            # In production, you would send an actual email
            # await self.email_service.send_verification_email(email, verification_token)

            return True

        except Exception as e:
            logger.error("Failed to send verification email", email=email, error=str(e))
            return False


class EmailVerificationService:
    """Service for managing email verification tokens."""

    def __init__(self):
        self.verification_tokens = {}  # In production, use Redis/database

    def generate_verification_token(self, email: str) -> str:
        """Generate a verification token for email."""
        import secrets
        token = secrets.token_urlsafe(32)

        # Store token with email (in production, use database with expiration)
        self.verification_tokens[token] = {
            "email": email,
            "created_at": datetime.utcnow(),
            "verified": False
        }

        return token

    def verify_token(self, token: str) -> Optional[str]:
        """Verify email verification token."""
        if token in self.verification_tokens:
            token_data = self.verification_tokens[token]

            # Check if token is expired (24 hours)
            if (datetime.utcnow() - token_data["created_at"]).total_seconds() > 86400:
                del self.verification_tokens[token]
                return None

            token_data["verified"] = True
            return token_data["email"]

        return None

    def is_email_verified(self, email: str) -> bool:
        """Check if email has been verified."""
        # In production, check database
        return any(
            data["email"] == email and data["verified"]
            for data in self.verification_tokens.values()
        )
