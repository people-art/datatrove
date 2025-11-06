"""
Email task for sending notifications
"""

import structlog
from app.worker import celery_app

logger = structlog.get_logger(__name__)


@celery_app.task(bind=True, name="app.tasks.email_task")
def email_task(self, email_type: str, recipient: str, data: dict):
    """
    Async task to send email notifications.

    Types: verification, order_confirmation, delivery_notification
    """
    logger.info("Starting email task", email_type=email_type, recipient=recipient, task_id=self.request.id)

    try:
        # In production, this would integrate with SendGrid/Postmark
        # For now, just log the email

        if email_type == "verification":
            logger.info("Sending verification email", recipient=recipient, token=data.get("token"))
        elif email_type == "order_confirmation":
            logger.info("Sending order confirmation", recipient=recipient, order_id=data.get("order_id"))
        elif email_type == "delivery_notification":
            logger.info("Sending delivery notification",
                       recipient=recipient,
                       hf_repo=data.get("hf_repo"),
                       private=data.get("private", True))

        # Simulate email sending delay
        import time
        time.sleep(1)

        logger.info("Email task completed", email_type=email_type, recipient=recipient)

        return {"status": "sent", "email_type": email_type, "recipient": recipient}

    except Exception as e:
        logger.error("Email task failed", email_type=email_type, recipient=recipient, error=str(e))
        raise self.retry(countdown=60, max_retries=3, exc=e)
