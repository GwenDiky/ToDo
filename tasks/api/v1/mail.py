import logging
import os

import aioboto3
from django.template.loader import get_template

logger = logging.getLogger(__name__)


class Mail:
    sender = os.getenv("EMAIL_HOST_USER")
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION_NAME = os.getenv("AWS_REGION_NAME")
    LOCALSTACK_ENDPOINT = os.getenv("LOCALSTACK_ENDPOINT")

    def __init__(self, recipient, subject, body):
        self.recipient = recipient
        self.subject = subject
        self.body = body
        self.ses_client = None
        self.template = get_template("html/notification_of_deadlines.html")
        self._is_sender_verified = False

    async def init_ses_client(self):
        if not self.ses_client:
            session = aioboto3.Session()
            async with session.client(
                "ses",
                aws_access_key_id=self.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=self.AWS_SECRET_ACCESS_KEY,
                region_name=self.AWS_REGION_NAME,
                endpoint_url=self.LOCALSTACK_ENDPOINT,
            ) as client:
                self.ses_client = client

    async def verify_sender(self):
        if not self._is_sender_verified:
            await self.init_ses_client()
            try:
                response = await self.ses_client.verify_email_identity(
                    EmailAddress=self.sender
                )
                logger.info(f"Sender {self.sender} verified: {response}")
                self._is_sender_verified = True
            except Exception as e:
                logger.error(f"Error verifying sender: {e}")

    async def send_email_notification(self, title_of_task):
        """Send email notification using SES"""
        logger.info(
            f"Preparing to send email from {self.sender} to {self.recipient}")

        # Render email template
        template = self.template.render({"task": title_of_task})

        try:
            await self.init_ses_client()  # Ensure SES client is initialized
            await self.verify_sender()  # Ensure sender is verified

            # Send the email
            response = await self.ses_client.send_email(
                Source=self.sender,
                Destination={"ToAddresses": [self.recipient]},
                Message={
                    "Subject": {"Data": self.subject, "Charset": "UTF-8"},
                    "Body": {"Html": {"Data": template, "Charset": "UTF-8"}},
                },
            )
            logger.info(f"Email successfully sent to {self.recipient}")
            return response

        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")

        finally:
            if self.ses_client:
                await self.ses_client.close()