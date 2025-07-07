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
    one_hour_from_now = current_time + timedelta(hours=1)
    return Task.objects.filter(
        is_notified=False,
        notification=True,
        deadline__lte=one_hour_from_now,
        deadline__gt=current_time,
    ).exclude(status="done")


@sync_to_async
def update_task(task_instance):
    task_instance.is_notified = True
    task_instance.save()


@sync_to_async
def count_tasks(task_queryset):
    return task_queryset.count()


@shared_task
def check_deadlines_and_notify_user():
    logger.info("Running task of email sending...")
    current_time = timezone.now()
    tasks = async_to_sync(get_tasks_to_notify)(current_time)

    task_count = async_to_sync(count_tasks)(tasks)
    logger.info("%s issues were found that need to be notified", task_count)

    for task in tasks:
        recipient_email = async_to_sync(get_email_of_user)(task.user_id)
        notification = Mail(
            recipient=recipient_email, subject="Task deadline approaching"
        )
        async_to_sync(notification.send_email_notification)(
            title_of_task=task.title
        )

        async_to_sync(update_task)(task)

        logger.info(
            "User with id '%s' was notified about the task '%s'",
            task.user_id,
            task.title,
        )
