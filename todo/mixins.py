# tasks/api/v1/mixins.py
from asgiref.sync import async_to_sync
from tasks.api.v1.utils import extract_file_info
from todo.api.v1.kafka_event_sender import KafkaEventSender
from tasks.api.v1.mail import Mail
from rest_framework.exceptions import ValidationError
from rest_framework import response, status
from tasks.models import Task
import logging

logger = logging.getLogger(__name__)

class FileEventMixin:
    def send_file_event(self, event_type, instance, attachment_url=None):
        if not attachment_url:
            attachment_url = instance.attachment_url

        if attachment_url:
            file_name, file_type = extract_file_info(attachment_url)
            file_instance = {
                "file_name": file_name,
                "file_type": file_type,
                "file_url": attachment_url,
            }
            KafkaEventSender.send_attachment_event(
                event_type=event_type, instance=file_instance
            )
            logger.info(f"Sent event '{event_type}' for file {attachment_url}")


class TaskNotificationMixin:
    def send_task_notification(self, user, task, new_status=None):
        if new_status and task.status != new_status:
            mail = Mail(
                recipient=async_to_sync(self.get_user_email)(user),
                subject="Status of task changed. Hurry up!",
            )
            async_to_sync(mail.send_email_notification)(
                task_title=task.title
            )

    def get_user_email(self, user):
        return async_to_sync(utils.get_email_of_user)(user)


class TaskCreateMixin:
    def perform_create(self, serializer):
        user_id, request_data = self.request.user, self.request.data

        if request_data.get("user_id"):
            recipient_email = async_to_sync(utils.get_email_of_user)(user_id)
            mail = Mail(
                recipient=recipient_email,
                subject="You were invited to a task. Please respond promptly!"
            )
            async_to_sync(mail.send_invitation_email)(
                task=request_data.get("title"),
                project=Project.objects.get(id=request_data.get("project"))
            )
        else:
            request_data["user_id"] = user_id

        logger.info("Creating task for user %s", user_id)
        serializer = self.get_serializer_class()(data=request_data)

        if serializer.is_valid():
            task = serializer.save()
            logger.info("Task created successfully: %s", task)

            if task.attachment_url:
                self.send_file_event(event_type="upload_file", instance=task)

            KafkaEventSender.send_task_event(
                event_type="task_created", instance=task, user_id=task.user_id
            )

            return response.Response(
                data=serializer.data, status=status.HTTP_201_CREATED
            )

        logger.error("Serializer errors: %s", serializer.errors)
        raise ValidationError(serializer.errors)


class TaskUpdateMixin(FileEventMixin, TaskNotificationMixin):
    def partial_update(self, request, *args, **kwargs) -> response.Response:
        user = self.request.user
        task = self.get_object()

        serializer = serializers.TaskUpdateSerializer(
            instance=task,
            data=request.data,
            context={"author": user},
            partial=True,
        )

        if serializer.is_valid():
            if "status" in serializer.validated_data:
                old_status = task.status
                new_status = serializer.validated_data["status"]
                self.send_task_notification(user, task, new_status)

            serializer.save()

            attachment_url = serializer.validated_data.get("attachment_url")

            if attachment_url:
                if task.attachment_url != attachment_url:
                    self.send_file_event(
                        event_type="update_file", instance=task,
                        attachment_url=attachment_url
                    )
            elif task.attachment_url and not attachment_url:
                self.send_file_event(
                    event_type="file_deleted", instance=task
                )

            KafkaEventSender.send_task_event(
                event_type="task_updated", instance=task, user_id=task.user_id
            )

            return response.Response(
                data=serializer.data, status=status.HTTP_200_OK
            )

        raise ValidationError(serializer.errors)


class TaskDestroyMixin(FileEventMixin):
    def destroy(self, request, *args, **kwargs) -> response.Response:
        task = self.get_object()
        if request.user == task.user_id:
            super().destroy(request, *args, **kwargs)
            if task.attachment_url:
                self.send_file_event(
                    event_type="delete_file", instance=task
                )
            KafkaEventSender.send_task_event(event_type="task_deleted",
                                             instance=task)
            return response.Response(status=status.HTTP_204_NO_CONTENT)
        raise exceptions.PermissionDeniedException
