"""
Email validation API endpoints
"""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.schemas import benchmark as schemas
from app.db.dependencies import get_db
from app.services.email_validation import EmailValidationService, EmailVerificationService
from app.core.errors import ValidationError, BusinessError, handle_business_error

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.post("/validate", response_model=schemas.EmailValidationResponse)
async def validate_email(
    data: schemas.EmailValidationRequest,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Validate email address format and domain.
    """
    try:
        validation_service = EmailValidationService()

        # Perform comprehensive email validation
        result = await validation_service.validate_email(data.email)

        logger.info("Email validation completed", email=data.email, valid=result["format_valid"])

        return schemas.EmailValidationResponse(
            email=result["email"],
            isValid=result["format_valid"] and result["mx_valid"],
            domain=result["domain"],
            checks={
                "format": result["format_valid"],
                "mx_records": result["mx_valid"],
                "smtp_connection": result["smtp_valid"],
                "disposable_domain": not result["is_disposable"]
            }
        )

    except (ValidationError, BusinessError) as e:
        logger.warning("Email validation failed", email=data.email, error=e.message)
        raise handle_business_error(e)
    except Exception as e:
        logger.error("Email validation error", email=data.email, error=str(e))
        raise HTTPException(status_code=500, detail="Email validation failed")


@router.post("/verify/send")
async def send_verification_email(
    data: schemas.EmailVerificationRequest,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Send email verification code/link.
    """
    try:
        validation_service = EmailValidationService()
        verification_service = EmailVerificationService()

        # First validate the email
        await validation_service.validate_email(data.email)

        # Generate verification token
        token = verification_service.generate_verification_token(data.email)

        # Send verification email
        success = await validation_service.send_verification_email(data.email, token)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to send verification email")

        logger.info("Verification email sent", email=data.email)

        return {
            "success": True,
            "message": "Verification email sent successfully"
        }

    except (ValidationError, BusinessError) as e:
        logger.warning("Email verification failed", email=data.email, error=e.message)
        raise handle_business_error(e)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Email verification error", email=data.email, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to send verification email")


@router.post("/verify/confirm")
async def confirm_email_verification(
    data: schemas.EmailVerificationConfirmRequest,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Confirm email verification with token.
    """
    try:
        verification_service = EmailVerificationService()

        # Verify the token
        verified_email = verification_service.verify_token(data.token)

        if not verified_email:
            raise ValidationError("Invalid or expired verification token")

        logger.info("Email verification confirmed", email=verified_email)

        return {
            "success": True,
            "email": verified_email,
            "message": "Email verified successfully"
        }

    except ValidationError as e:
        logger.warning("Email verification confirmation failed", error=e.message)
        raise handle_business_error(e)
    except Exception as e:
        logger.error("Email verification confirmation error", error=str(e))
        raise HTTPException(status_code=500, detail="Email verification failed")
