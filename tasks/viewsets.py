import logging

from asgiref.sync import async_to_sync
from django.db.models.query import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters as drf_filters
from rest_framework import mixins, response, status, viewsets

from projects.models import Project
from tasks import exceptions
from tasks.api.v1 import filters, serializers, utils
from tasks.api.v1.mail import Mail
from tasks.api.v1.utils import extract_file_info
from tasks.models import Task
from todo.api.v1 import kafka_producer
from todo.jwt_auth import IsAuthenticatedById, JWTAuthenticationCustom
from todo.api.v1.kafka_event_sender import KafkaEventSender


logger = logging.getLogger(__name__)


class TaskListMixin(mixins.ListModelMixin):
    def get_queryset(self) -> QuerySet[Task]:
        return Task.objects.filter(user_id=self.request.user)


class TaskCreateMixin(mixins.CreateModelMixin):
    def perform_create(self, serializer):
        user_id, request_data = self.request.user, self.request.data

        if request_data.get("user_id"):
            recipient_email = async_to_sync(utils.get_email_of_user)(user_id)
            mail = Mail(
                recipient=recipient_email,
                subject="You were invited to a task. Please respond promptly!",
            )
            async_to_sync(mail.send_invitation_email)(
                task=request_data.get("title"),
                project=Project.objects.get(id=request_data.get("project")),
            )
        else:
            request_data["user_id"] = user_id

        logger.info("Creating task for user %s", user_id)
        serializer = self.get_serializer_class()(data=request_data)

        if serializer.is_valid():
            task = serializer.save()
            logger.info("Task created successfully: %s", task)

            if task.attachment_url:
                file_name, file_type = extract_file_info(task.attachment_url)
                file_instance = {
                    "file_name": file_name,
                    "file_type": file_type,
                    "file_url": task.attachment_url,
                }
                KafkaEventSender.send_attachment_event(
                    event_type="upload_file", instance=file_instance
                )
            KafkaEventSender.send_task_event(
                event_type="task_created", instance=task, user_id=task.user_id
            )
            return response.Response(
                data=serializer.data, status=status.HTTP_201_CREATED
            )

        logger.error("Serializer errors: %s", serializer.errors)
        raise ValidationError(serializer.errors)

class TaskUpdateMixin(mixins.UpdateModelMixin):
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
                if old_status != new_status:
                    if task.notification:
                        mail = Mail(
                            recipient=async_to_sync(utils.get_email_of_user)(
                                user
                            ),
                            subject="Status of task changed. Hurry up!",
                        )
                        async_to_sync(mail.send_email_notification)(
                            task_title=serializer.validated_data["title"]
                        )

            serializer.save()

            attachment_url = serializer.validated_data.get("attachment_url")

            if attachment_url:
                if task.attachment_url != attachment_url:
                    file_name, file_type = extract_file_info(attachment_url)
                    file_instance = {
                        "file_name": file_name,
                        "file_type": file_type,
                        "file_url": attachment_url,
                    }
                    KafkaEventSender.send_attachment_event(
                        event_type="update_file", instance=file_instance
                    )
            elif task.attachment_url and not attachment_url:
                KafkaEventSender.send_attachment_event(
                    event_type="file_deleted",
                    instance={"file_url": task.attachment_url},
                )

            KafkaEventSender.send_task_event(
                event_type="task_updated", instance=task, user_id=task.user_id
            )

            return response.Response(
                data=serializer.data, status=status.HTTP_200_OK
            )

        raise ValidationError(serializer.errors)

class TaskDestroyMixin(mixins.DestroyModelMixin):
    def destroy(self, request, *args, **kwargs) -> response.Response:
        task = self.get_object()
        if request.user == task.user_id:
            super().destroy(request, *args, **kwargs)
            if task.attachment_url:
                file_name, file_type = extract_file_info(task.attachment_url)
                attachment_instance = {
                    "file_name": file_name,
                    "file_type": file_type,
                    "file_url": task.attachment_url,
                }
                KafkaEventSender.send_attachment_event(
                    event_type="delete_file", instance=attachment_instance
                )
            KafkaEventSender.send_task_event(event_type="task_deleted", instance=task)
            return response.Response(status=status.HTTP_204_NO_CONTENT)
        raise exceptions.PermissionDeniedException


class TaskViewSet(
    viewsets.GenericViewSet,
    TaskCreateMixin,
    TaskListMixin,
    TaskUpdateMixin,
    TaskDestroyMixin,
):
    queryset = Task.objects.all().order_by("-pk")

    serializer_class_map = {
        "default": serializers.TaskSerializer,
        "create": serializers.TaskCreateSerializer,
        "update": serializers.TaskUpdateSerializer,
        "partial_update": serializers.TaskUpdateSerializer,
        "list": serializers.TaskListSerializer,
    }

    def get_serializer_class(self):
        action = self.action
        if action in self.serializer_class_map:
            return self.serializer_class_map[action]
        return self.serializer_class_map["default"]

    filter_backends = (DjangoFilterBackend, drf_filters.OrderingFilter)
    filterset_class = filters.FilterTasks
    ordering = ["created_at"]
    ordering_fields = ["title", "created_at"]

    authentication_classes = [JWTAuthenticationCustom]
    permission_classes = [IsAuthenticatedById]
