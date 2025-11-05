"""
Email service for sending notifications
"""

import asyncio
from typing import Optional
import structlog

try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, Email, To, Content
except ImportError:
    SendGridAPIClient = None
    Mail = None
    Email = None
    To = None
    Content = None

from app.core.config import settings

logger = structlog.get_logger(__name__)


class EmailService:
    """Service for sending email notifications."""

    def __init__(self):
        if SendGridAPIClient and settings.SENDGRID_API_KEY:
            self.sg = SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
        else:
            self.sg = None
            logger.warning("SendGrid not configured - email notifications disabled")

    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> bool:
        """Send email using SendGrid."""

        if not self.sg:
            logger.warning("Email service not available - skipping email send")
            return False

        try:
            from_email = Email(settings.EMAIL_FROM, settings.EMAIL_FROM_NAME)
            to_email_obj = To(to_email)

            # Create plain text content
            content = Content("text/plain", body)

            # Create HTML content if provided
            if html_body:
                from sendgrid.helpers.mail import Content as HtmlContent
                html_content = HtmlContent("text/html", html_body)
                mail = Mail(from_email, to_email_obj, subject, html_content)
                mail.add_content(content)  # Add plain text as alternative
            else:
                mail = Mail(from_email, to_email_obj, subject, content)

            # Send email
            response = self.sg.send(mail)

            if response.status_code in [200, 201, 202]:
                logger.info(
                    "Email sent successfully",
                    to=to_email,
                    subject=subject,
                    status_code=response.status_code
                )
                return True
            else:
                logger.error(
                    "Email send failed",
                    to=to_email,
                    status_code=response.status_code,
                    response_body=response.body
                )
                return False

        except Exception as e:
            logger.error(
                "Email send error",
                to=to_email,
                subject=subject,
                error=str(e)
            )
            return False

    async def send_order_confirmation(self, order_id: str, email: str, order_details: dict) -> bool:
        """Send order confirmation email."""

        subject = f"FineData Order Confirmation - {order_id}"

        body = f"""
Dear Customer,

Thank you for your order! Your dataset generation request has been received and is being processed.

Order Details:
- Order ID: {order_id}
- Domain: {order_details.get('domain', 'N/A')}
- Quality Tier: {order_details.get('quality_tier', 'N/A')}
- Estimated Cost: ${order_details.get('total', 0):.2f}

Next Steps:
1. We'll run a benchmark preview (usually completes in 5-10 minutes)
2. Review the quality metrics and pricing
3. Confirm payment to start full production processing
4. Receive delivery notification via email

You can track your order progress at:
http://localhost:3000/order/{order_id}

If you have any questions, please contact support@finedata.example.com

Best regards,
The FineData Team
"""

        return await self.send_email(email, subject, body)

    async def send_benchmark_ready(self, order_id: str, email: str, benchmark_results: dict) -> bool:
        """Send benchmark completion notification."""

        subject = f"FineData Benchmark Complete - {order_id}"

        body = f"""
Dear Customer,

Your benchmark analysis is complete! Here are the quality metrics for your dataset:

Quality Metrics:
- Coverage: {benchmark_results.get('coverage', 0):.1%}
- Quality Pass Rate: {benchmark_results.get('quality_pass_rate', 0):.1%}
- Documents Found: {benchmark_results.get('docs_kept', 0):,}
- Estimated Tokens: {benchmark_results.get('tokens', 0):,}

Pricing:
- Subtotal: ${benchmark_results.get('subtotal', 0):.2f}
- Tax: ${benchmark_results.get('tax', 0):.2f}
- Total: ${benchmark_results.get('total', 0):.2f}

Next Step:
Please review the results and proceed with payment to start full production processing.

Review your benchmark at:
http://localhost:3000/order/{order_id}

Best regards,
The FineData Team
"""

        return await self.send_email(email, subject, body)

    async def send_payment_confirmation(self, order_id: str, email: str, payment_details: dict) -> bool:
        """Send payment confirmation email."""

        subject = f"FineData Payment Confirmed - {order_id}"

        body = f"""
Dear Customer,

Your payment has been successfully processed! Production processing has begun.

Payment Details:
- Order ID: {order_id}
- Amount Paid: ${payment_details.get('amount', 0):.2f}
- Processing Time: 2-4 hours (depending on dataset size)

What happens next:
1. Your data will be processed on our Slurm cluster
2. Quality filtering, deduplication, and privacy protection will be applied
3. The final dataset will be uploaded to a private HuggingFace repository
4. You'll receive a delivery notification with access instructions

Track progress at:
http://localhost:3000/order/{order_id}

Best regards,
The FineData Team
"""

        return await self.send_email(email, subject, body)

    async def send_processing_update(self, order_id: str, email: str, progress: dict) -> bool:
        """Send processing progress update."""

        subject = f"FineData Processing Update - {order_id}"

        body = f"""
Dear Customer,

Your dataset is currently being processed. Here's the latest progress:

Processing Status:
- Documents Processed: {progress.get('fetched', 0):,}
- Documents Filtered: {progress.get('filtered', 0):,}
- Documents Deduplicated: {progress.get('deduped', 0):,}
- Tokens Generated: {progress.get('tokens', 0):,}
- Estimated Completion: {progress.get('eta', 'Unknown')}

Track detailed progress at:
http://localhost:3000/order/{order_id}

Best regards,
The FineData Team
"""

        return await self.send_email(email, subject, body)

    async def send_delivery_notification(
        self,
        order_id: str,
        email: str,
        delivery_info: dict
    ) -> bool:
        """Send dataset delivery notification."""

        subject = f"Your FineData Dataset is Ready! - {order_id}"

        body = f"""
Dear Customer,

🎉 Your custom dataset has been successfully processed and delivered!

Dataset Details:
- Order ID: {order_id}
- Dataset URL: {delivery_info.get('hf_url', 'N/A')}
- Dataset Card: {delivery_info.get('dataset_card', 'N/A')}
- Invoice: {delivery_info.get('invoice_url', 'N/A')}

Important Notes:
- The dataset is stored in a private HuggingFace repository
- Access is restricted to your account only
- The dataset may only be used for internal training purposes
- All PII has been removed and content has been sanitized

To access your dataset:
1. Visit the HuggingFace URL provided above
2. Log in with your HuggingFace account
3. Download or use the dataset directly

If you need to share access with team members or have any questions, please contact support@finedata.example.com

Thank you for choosing FineData!

Best regards,
The FineData Team
"""

        return await self.send_email(email, subject, body)

    async def send_failure_notification(
        self,
        order_id: str,
        email: str,
        error_message: str,
        failure_type: str = "processing"
    ) -> bool:
        """Send failure notification email."""

        subject = f"FineData {failure_type.title()} Failed - {order_id}"

        body = f"""
Dear Customer,

We're sorry to inform you that there was an issue with your order processing.

Order Details:
- Order ID: {order_id}
- Issue Type: {failure_type.title()}

Error Details:
{error_message}

What to do next:
1. Visit your order page: http://localhost:3000/order/{order_id}
2. Contact our support team for assistance
3. We may be able to retry the processing or provide a refund

Our support team is available at support@finedata.example.com and will help resolve this issue as quickly as possible.

We apologize for any inconvenience this may have caused.

Best regards,
The FineData Team
"""

        return await self.send_email(email, subject, body)
