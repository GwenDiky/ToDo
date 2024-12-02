import logging

from asgiref.sync import async_to_sync
from django.db.models.query import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters as drf_filters
from rest_framework import response, status, viewsets

from projects.models import Project
from tasks.api.v1 import filters, serializers, utils
from tasks.api.v1.mail import Mail
from tasks.models import Task
from todo.jwt_auth import IsAuthenticatedById, JWTAuthenticationCustom
from todo.viewsets import StandardPaginationViewSet

logger = logging.getLogger(__name__)


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all().order_by("-pk")

    serializer_class = serializers.TaskSerializer

    filter_backends = (DjangoFilterBackend, drf_filters.OrderingFilter)

    filterset_class = filters.FilterTasks
    ordering = ["created_at"]
    pagination_class = StandardPaginationViewSet
    ordering_fields = ["title", "created_at"]

    authentication_classes = [JWTAuthenticationCustom]
    permission_classes = [IsAuthenticatedById]

    def get_queryset(self) -> QuerySet[Task]:
        return Task.objects.filter(user_id=self.request.user)

    def create(self, request, *args, **kwargs) -> response.Response:
        user_id, request_data = request.user, request.data

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
        serializer = self.serializer_class(data=request_data)

        if serializer.is_valid():
            serializer.save()
            return response.Response(
                data=serializer.data, status=status.HTTP_201_CREATED
            )
        return response.Response(
            data=serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )

    def partial_update(self, request, *args, **kwargs) -> response.Response:
        user = self.request.user
        task = self.get_object()
        task.user_id = user

        serializer = self.serializer_class(
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
                            title_of_task=serializer.validated_data["title"]
                        )
            serializer.save()
            return response.Response(
                data=serializer.data, status=status.HTTP_200_OK
            )
        logger.error("Invalid data: %s", serializer.errors)
        return response.Response(
            data=serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )

    def perform_destroy(self, request, *args, **kwargs) -> response.Response:
        task = self.get_object()
        if request.user == task.user_id:
            super().destroy(request, *args, **kwargs)
            return response.Response(status=status.HTTP_204_NO_CONTENT)
        return response.Response(
            data="Permission denied", status=status.HTTP_403_FORBIDDEN
        )
