"""
Email service for sending notifications and verification emails
"""

import uuid
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import structlog
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

from app.core.config import settings
from app.core.errors import AppError, ErrorCode

logger = structlog.get_logger(__name__)


class EmailService:
    """Service for sending emails"""

    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER or "smtp.gmail.com"
        self.smtp_port = settings.SMTP_PORT or 587
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.FROM_EMAIL or "noreply@finedata.ai"
        self.from_name = settings.FROM_NAME or "FineData"

    def _create_verification_token(self) -> str:
        """Generate a secure verification token"""
        return str(uuid.uuid4())

    def _send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """Send an email via SMTP"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email

            # Add text content
            if text_content:
                msg.attach(MIMEText(text_content, 'plain'))

            # Add HTML content
            msg.attach(MIMEText(html_content, 'html'))

            # Send email
            if self.smtp_username and self.smtp_password:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.sendmail(self.from_email, to_email, msg.as_string())
                server.quit()
                logger.info("Email sent successfully", to=to_email, subject=subject)
                return True
            else:
                # For development/testing - just log
                logger.info("Email would be sent (SMTP not configured)", to=to_email, subject=subject)
                return True

        except Exception as e:
            logger.error("Failed to send email", error=str(e), to=to_email)
            raise AppError(
                f"Failed to send email: {str(e)}",
                ErrorCode.DELIVERY_EMAIL_FAILED,
                details={"to": to_email, "subject": subject}
            )

    def send_verification_email(self, email: str, verification_token: str) -> bool:
        """Send email verification link"""
        verification_url = f"{settings.FRONTEND_URL}/verify-email?token={verification_token}"

        subject = "Verify your email - FineData"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Verify your email</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h1 style="color: #2D5BFF;">Welcome to FineData!</h1>

                <p>Please verify your email address to continue creating custom datasets.</p>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="{verification_url}"
                       style="background-color: #2D5BFF; color: white; padding: 12px 24px;
                              text-decoration: none; border-radius: 6px; display: inline-block;">
                        Verify Email Address
                    </a>
                </div>

                <p>If the button doesn't work, copy and paste this link into your browser:</p>
                <p style="word-break: break-all; background-color: #f5f5f5; padding: 10px; border-radius: 4px;">
                    {verification_url}
                </p>

                <p>This verification link will expire in 24 hours.</p>

                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">

                <p style="color: #666; font-size: 14px;">
                    If you didn't request this email, you can safely ignore it.
                </p>

                <p style="color: #666; font-size: 14px;">
                    Best regards,<br>
                    The FineData Team
                </p>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Welcome to FineData!

        Please verify your email address by clicking this link:
        {verification_url}

        This verification link will expire in 24 hours.

        If you didn't request this email, you can safely ignore it.

        Best regards,
        The FineData Team
        """

        return self._send_email(email, subject, html_content, text_content)

    def send_dataset_ready_email(
        self,
        email: str,
        order_id: str,
        hf_repo_url: str,
        dataset_info: Dict[str, Any]
    ) -> bool:
        """Send dataset delivery notification"""
        subject = f"Your FineData dataset is ready - Order {order_id}"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Your dataset is ready</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h1 style="color: #12B886;">Your Dataset is Ready!</h1>

                <p>Great news! Your custom domain dataset has been processed and is now available.</p>

                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3>Dataset Details:</h3>
                    <ul>
                        <li><strong>Order ID:</strong> {order_id}</li>
                        <li><strong>Domain:</strong> {dataset_info.get('domain', 'N/A')}</li>
                        <li><strong>Quality Tier:</strong> {dataset_info.get('quality_tier', 'N/A')}</li>
                        <li><strong>Languages:</strong> {', '.join(dataset_info.get('languages', []))}</li>
                        <li><strong>Estimated Size:</strong> {dataset_info.get('estimated_tokens', 'N/A')} tokens</li>
                    </ul>
                </div>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="{hf_repo_url}"
                       style="background-color: #12B886; color: white; padding: 12px 24px;
                              text-decoration: none; border-radius: 6px; display: inline-block;">
                        Access Your Dataset
                    </a>
                </div>

                <h3>How to Access Your Dataset:</h3>
                <ol>
                    <li>Click the "Access Your Dataset" button above</li>
                    <li>Sign in to your Hugging Face account (or create one if you don't have one)</li>
                    <li>The dataset will be available in your private repository</li>
                    <li>Use the Hugging Face datasets library to load your data:
                        <code style="background-color: #f5f5f5; padding: 2px 4px; border-radius: 3px;">
                            from datasets import load_dataset<br>
                            dataset = load_dataset("{hf_repo_url}")
                        </code>
                    </li>
                </ol>

                <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 15px;
                           border-radius: 6px; margin: 20px 0;">
                    <strong>Important:</strong> This dataset is private and contains watermarking for verification purposes.
                    Please review our terms of service regarding data usage and privacy.
                </div>

                <p>Need help? Contact our support team at support@finedata.ai</p>

                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">

                <p style="color: #666; font-size: 14px;">
                    Thank you for choosing FineData!<br>
                    Best regards,<br>
                    The FineData Team
                </p>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Your Dataset is Ready!

        Great news! Your custom domain dataset has been processed and is now available.

        Dataset Details:
        - Order ID: {order_id}
        - Domain: {dataset_info.get('domain', 'N/A')}
        - Quality Tier: {dataset_info.get('quality_tier', 'N/A')}
        - Languages: {', '.join(dataset_info.get('languages', []))}
        - Estimated Size: {dataset_info.get('estimated_tokens', 'N/A')} tokens

        Access your dataset here: {hf_repo_url}

        How to use your dataset:
        1. Click the link above
        2. Sign in to Hugging Face (or create an account)
        3. The dataset is in your private repository
        4. Load with: from datasets import load_dataset; dataset = load_dataset("{hf_repo_url}")

        Important: This dataset is private and contains watermarking for verification.
        Please review our terms of service.

        Need help? Contact support@finedata.ai

        Thank you for choosing FineData!
        Best regards,
        The FineData Team
        """

        return self._send_email(email, subject, html_content, text_content)

    def send_payment_failed_email(self, email: str, order_id: str, reason: str) -> bool:
        """Send payment failure notification"""
        subject = f"Payment Failed - Order {order_id}"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Payment Failed</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h1 style="color: #EF4444;">Payment Failed</h1>

                <p>We're sorry, but your payment for order {order_id} could not be processed.</p>

                <div style="background-color: #fef2f2; border: 1px solid #fecaca; padding: 15px;
                           border-radius: 6px; margin: 20px 0;">
                    <strong>Reason:</strong> {reason}
                </div>

                <p>You can try again by visiting your order page or contact our support team for assistance.</p>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="{settings.FRONTEND_URL}/orders/{order_id}"
                       style="background-color: #EF4444; color: white; padding: 12px 24px;
                              text-decoration: none; border-radius: 6px; display: inline-block;">
                        Retry Payment
                    </a>
                </div>

                <p>If you need help, please contact support@finedata.ai</p>

                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">

                <p style="color: #666; font-size: 14px;">
                    Best regards,<br>
                    The FineData Team
                </p>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Payment Failed

        We're sorry, but your payment for order {order_id} could not be processed.

        Reason: {reason}

        You can try again by visiting your order page or contact our support team for assistance.

        Order page: {settings.FRONTEND_URL}/orders/{order_id}

        If you need help, please contact support@finedata.ai

        Best regards,
        The FineData Team
        """

        return self._send_email(email, subject, html_content, text_content)


# Global instance
email_service = EmailService()


def get_email_service() -> EmailService:
    """Dependency injection for email service"""
    return email_service