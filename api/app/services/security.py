"""
Security service for data protection and access control
"""

import hashlib
import hmac
import secrets
import time
from typing import Optional, Dict, Any
from urllib.parse import urlencode
import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)


class SecurityService:
    """Service for implementing security measures and data protection."""

    def __init__(self):
        self.secret_key = settings.SECRET_KEY.encode() if settings.SECRET_KEY else secrets.token_bytes(32)

    def generate_signed_url(
        self,
        base_url: str,
        expires_in: int = 3600,  # 1 hour
        **params
    ) -> str:
        """Generate a signed URL with expiration."""

        # Add expiration timestamp
        expires = int(time.time()) + expires_in
        params['expires'] = str(expires)

        # Create parameter string
        param_string = urlencode(sorted(params.items()))

        # Generate signature
        signature = self._generate_signature(f"{base_url}?{param_string}")

        # Add signature to params
        params['signature'] = signature

        # Re-encode with signature
        final_param_string = urlencode(sorted(params.items()))

        return f"{base_url}?{final_param_string}"

    def verify_signed_url(self, url: str, base_url: str) -> bool:
        """Verify a signed URL."""

        try:
            # Parse URL and extract parameters
            if '?' not in url:
                return False

            url_part, param_string = url.split('?', 1)
            if url_part != base_url:
                return False

            # Parse parameters
            params = dict(param.split('=', 1) for param in param_string.split('&') if '=' in param)

            # Extract signature and expiration
            signature = params.pop('signature', None)
            expires_str = params.pop('expires', None)

            if not signature or not expires_str:
                return False

            # Check expiration
            try:
                expires = int(expires_str)
                if time.time() > expires:
                    logger.warning("Signed URL expired", expires=expires)
                    return False
            except ValueError:
                return False

            # Verify signature
            expected_signature = self._generate_signature(f"{base_url}?{urlencode(sorted(params.items()))}")

            return hmac.compare_digest(signature, expected_signature)

        except Exception as e:
            logger.error("URL verification failed", error=str(e))
            return False

    def _generate_signature(self, data: str) -> str:
        """Generate HMAC signature for data."""

        return hmac.new(
            self.secret_key,
            data.encode(),
            hashlib.sha256
        ).hexdigest()

    def sanitize_content(self, text: str) -> str:
        """Sanitize text content for safe storage and display."""

        # Remove or mask potential PII patterns
        import re

        # Email addresses
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL_MASKED]', text)

        # Phone numbers (various formats)
        text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE_MASKED]', text)

        # Social security numbers
        text = re.sub(r'\b\d{3}[-]?\d{2}[-]?\d{4}\b', '[SSN_MASKED]', text)

        # Credit card numbers
        text = re.sub(r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b', '[CARD_MASKED]', text)

        # IP addresses
        text = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '[IP_MASKED]', text)

        return text

    def add_watermark(self, data: Dict[str, Any], order_id: str) -> Dict[str, Any]:
        """Add watermark/metadata to dataset for tracking."""

        watermark = {
            "_finedata_metadata": {
                "order_id": order_id,
                "generated_by": "FineData",
                "version": "1.0.0",
                "license": "internal-use-only",
                "contact": "support@finedata.example.com",
                "generated_at": int(time.time()),
            }
        }

        # Merge watermark with data
        if isinstance(data, dict):
            data.update(watermark)

        return data

    def validate_api_key(self, api_key: str) -> bool:
        """Validate API key (placeholder for future implementation)."""

        # In production, this would check against a database of valid API keys
        # For now, just check if it's not empty
        return bool(api_key and len(api_key.strip()) > 10)

    def rate_limit_check(self, client_id: str, endpoint: str, max_requests: int = 100, window_seconds: int = 3600) -> bool:
        """Check if request should be rate limited."""

        # This is a placeholder - in production, you'd use Redis or another store
        # to track request counts per client/endpoint

        # For now, always allow (no rate limiting)
        return True

    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data."""

        # This is a placeholder - in production, use proper encryption
        # For now, just return the data (in production, this would encrypt)
        logger.warning("Encryption not implemented - using plain text")
        return data

    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data."""

        # This is a placeholder - in production, use proper decryption
        # For now, just return the data (in production, this would decrypt)
        logger.warning("Decryption not implemented - returning plain text")
        return encrypted_data

    def generate_secure_token(self, length: int = 32) -> str:
        """Generate a secure random token."""

        return secrets.token_urlsafe(length)

    def hash_password(self, password: str) -> str:
        """Hash password for storage."""

        # This is a placeholder - in production, use proper password hashing
        # For now, just return a simple hash
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash."""

        # This is a placeholder - in production, use proper password verification
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest() == hashed_password

    def log_security_event(self, event_type: str, details: Dict[str, Any], severity: str = "info"):
        """Log security-related events."""

        log_data = {
            "event_type": event_type,
            "severity": severity,
            "timestamp": int(time.time()),
            **details
        }

        if severity == "error":
            logger.error("Security event", **log_data)
        elif severity == "warning":
            logger.warning("Security event", **log_data)
        else:
            logger.info("Security event", **log_data)

    def check_content_safety(self, text: str) -> Dict[str, Any]:
        """Check content for safety and compliance."""

        # This is a placeholder - in production, you might use AI models
        # to detect toxic content, hate speech, etc.

        issues = []

        # Simple checks for demonstration
        toxic_words = ['hate', 'violence', 'offensive']
        for word in toxic_words:
            if word.lower() in text.lower():
                issues.append({
                    "type": "potential_toxic_content",
                    "word": word,
                    "severity": "medium"
                })

        # Check for excessive caps
        caps_ratio = sum(1 for c in text if c.isupper()) / len(text) if text else 0
        if caps_ratio > 0.3:
            issues.append({
                "type": "excessive_capitalization",
                "ratio": caps_ratio,
                "severity": "low"
            })

        return {
            "safe": len(issues) == 0,
            "issues": issues,
            "risk_score": min(1.0, len(issues) * 0.2)
        }

    def audit_log(self, action: str, user_id: Optional[str], resource: str, details: Dict[str, Any]):
        """Create audit log entry."""

        audit_entry = {
            "timestamp": int(time.time()),
            "action": action,
            "user_id": user_id,
            "resource": resource,
            "ip_address": None,  # Would be populated from request
            "user_agent": None,  # Would be populated from request
            **details
        }

        logger.info("Audit log", **audit_entry)

        # In production, this would be stored in a database table
