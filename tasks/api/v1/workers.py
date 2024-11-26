import logging
from datetime import timedelta

from asgiref.sync import async_to_sync, sync_to_async
from celery import shared_task
from django.utils import timezone

from tasks.api.v1.mail import Mail
from tasks.api.v1.utils import get_email_of_user
from tasks.models import Task

logger = logging.getLogger(__name__)


@sync_to_async
def get_tasks_to_notify(current_time):
    return Task.objects.filter(
        is_notified=False,
        notification=True,
        deadline__lte=current_time + timedelta(hours=1),
        deadline__gt=current_time,
    ).exclude(status="done")


@sync_to_async
def save_task(task):
    task.save()


@sync_to_async
def count_tasks(tasks):
    return tasks.count()


@shared_task
def check_deadlines_and_notify():
    logger.info("Running task of email sending...")
    current_time = timezone.now()
    tasks = async_to_sync(get_tasks_to_notify)(current_time)

    task_count = async_to_sync(count_tasks)(tasks)
    logger.info("%s issues were found that need to be notified", task_count)

    for task in tasks:
        mail_of_recipient = async_to_sync(get_email_of_user)(task.user_id)
        mail = Mail(
            recipient=mail_of_recipient,
            subject="Test Email via SES and LocalStack",
        )
        logger.info(f"Working with the task: {task.title}")
        async_to_sync(mail.send_email_notification)(title_of_task=task.title)

        task.is_notified = True
        async_to_sync(save_task)(task)

        logger.info(
            f"User with id '%s' was notified about the task '%s'",
            task.user_id,
            task.title,
        )
