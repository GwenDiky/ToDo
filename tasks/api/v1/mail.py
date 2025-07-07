import logging

import aioboto3
from django.conf import settings
from django.template.loader import get_template

from projects.models import Project
from tasks import exceptions
from tasks.models import Task

logger = logging.getLogger(__name__)


class Mail:
    sender = settings.EMAIL_HOST_USER
    AWS_ACCESS_KEY_ID = settings.AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY = settings.AWS_SECRET_ACCESS_KEY
    AWS_REGION_NAME = settings.AWS_REGION_NAME
    LOCALSTACK_ENDPOINT = settings.LOCALSTACK_ENDPOINT

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
        if self._is_sender_verified:
            return

        await self.init_ses_client()
        try:
            result = await self.ses_client.verify_email_identity(
                EmailAddress=self.sender
            )
            logger.info("Sender %s verified: %s", self.sender, result)
            self._is_sender_verified = True
        except exceptions.EmailVerificationFailedException as error:
            logger.error("Failed to verify sender: %s", error.detail)
            return error.as_response()

    async def send_email_notification(
        self, task_title: str | None = None, email_template=None
    ):

        logger.info(
            "Preparing to send email from %s to %s",
            self.sender,
            self.recipient,
        )

        if not email_template:
            email_template = self.template.render(
                {"task": task_title} if task_title else None
            )

        try:
            await self.init_ses_client()
            if not self._is_sender_verified:
                await self.verify_sender()

            response = await self.ses_client.send_email(
                Source=self.sender,
                Destination={"ToAddresses": [self.recipient]},
                Message={
                    "Subject": {"Data": self.subject, "Charset": "UTF-8"},
                    "Body": {
                        "Html": {"Data": email_template, "Charset": "UTF-8"}
                    },
                },
            )
            logger.info("Email successfully sent to %s", self.recipient)
            return response

        except exceptions.EmailSendingFailedException as e:
            logger.error("Failed to send email: %s", e.detail)
            return e.as_response()

        finally:
            if self.ses_client:
                await self.ses_client.close()

    async def send_invitation_email(self, task: Task, project: Project):
        logger.info(
            "Preparing to send email from %s to %s",
            self.sender,
            self.recipient,
        )
        self.template = get_template("html/invitation.html")
        context = {
            "task_title": task.title,
            "project_title": project.title,
            "recipient_email": self.recipient,
        }
        template = self.template.render(context)
        await self.send_email_notification(email_template=template)
