import logging
import os

import aioboto3
from django.template.loader import get_template
from projects.models import Project
from tasks.models import Task
from tasks.api.v1 import exceptions

logger = logging.getLogger(__name__)


class Mail:
    sender = os.getenv("EMAIL_HOST_USER")
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION_NAME = os.getenv("AWS_REGION_NAME")
    LOCALSTACK_ENDPOINT = os.getenv("LOCALSTACK_ENDPOINT")

    def __init__(self, recipient, subject):
        self.recipient = recipient
        self.subject = subject
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
            except exceptions.EmailVerificationFailedException as e:
                logger.error(f"Error verifying sender: {e.detail}")
                return e.as_response()

    async def send_email_notification(self, title_of_task: str = None, template=None):
        logger.info(f"Preparing to send email from {self.sender} to {self.recipient}")

        if not template:
            template = self.template.render(
                {"task": title_of_task} if title_of_task else None
            )

        try:
            await self.init_ses_client()
            await self.verify_sender()

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

        except exceptions.EmailSendingFailedException as e:
            logger.error(f"Failed to send email: {e.detail}")
            return e.as_response()

        finally:
            if self.ses_client:
                await self.ses_client.close()

    async def send_invitation_email(self, task: Task, project: Project):
        logger.info(f"Preparing to send email from {self.sender} to {self.recipient}")

        self.template = get_template("html/invitation.html")
        template = self.template.render(
            {
                "task": task.title,
                "project": project.title,
                "email_address_of_consumer": self.recipient,
            }
        )

        await self.send_email_notification(template=template)
