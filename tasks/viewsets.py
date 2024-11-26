import logging

from asgiref.sync import async_to_sync
from django.db.models.query import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters as drf_filters
from rest_framework import response, status, viewsets
from rest_framework.exceptions import NotAuthenticated

from projects.models import Project
from tasks.api.v1 import filters, serializers, utils
from tasks.api.v1.mail import Mail
from tasks.models import Task
from todo.jwt_auth import IsAuthenticatedById, JWTAuthenticationCustom
from todo.viewsets import StandardPaginationViewSet

logger = logging.getLogger(__name__)


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all().order_by("-created_at")

    serializer_class = serializers.TaskSerializer

    filter_backends = (DjangoFilterBackend, drf_filters.OrderingFilter)

    filterset_class = filters.FilterTasks
    ordering = ["created_at"]
    pagination_class = StandardPaginationViewSet
    ordering_fields = ["title", "created_at"]

    authentication_classes = [JWTAuthenticationCustom]
    permission_classes = [IsAuthenticatedById]

    def get_queryset(self) -> QuerySet[Task]:
        if self.request.user:
            user_id = self.request.user
        else:
            raise NotAuthenticated("User is not authenticated.")
        return Task.objects.filter(user_id=user_id)

    def retrieve(self, request, pk=None) -> response.Response:
        instance = self.get_object()
        return response.Response(
            self.serializer_class(instance).data, status=status.HTTP_200_OK
        )

    def create(self, request, *args, **kwargs) -> response.Response:
        user, data = request.user, request.data

        if data.get("user_id"):
            mail_of_recipient = async_to_sync(utils.get_email_of_user)(user)

            mail = Mail(
                recipient=mail_of_recipient,
                subject="U was invited to task. Hurry up!",
            )
            async_to_sync(mail.send_invitation_email)(
                task=data.get("title"),
                project=Project.objects.get(id=data.get("project")),
            )
        else:
            data.update({"user_id": user})

        logger.info("Creating task for user %s", user)

        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save()
            return response.Response(
                data=serializer.data, status=status.HTTP_201_CREATED
            )
        else:
            return response.Response(
                data=serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

    def partial_update(self, request, pk=None, *args, **kwargs) -> response.Response:
        user = self.request.user
        instance = self.get_object()
        instance.user_id = user

        data = request.data

        logger.info(
            "Changing task with title: %s",
            data.get('title', 'No title provided')
        )

        if "status" in data:
            if data["status"] != instance.status:
                logger.info(
                    "Status of task '%s' changed from %s to %s",
                    instance.title,
                    instance.status,
                    data['status']
                )
                if instance.notification:
                    mail_of_recipient = async_to_sync(utils.get_email_of_user)(user)
                    mail = Mail(
                        recipient=mail_of_recipient,
                        subject="Status of task changed. Hurry up!",
                    )
                    async_to_sync(mail.send_email_notification)(
                        title_of_task=data["title"]
                    )

        serializer = self.serializer_class(
            instance=instance, data=data, context={"author": user}, partial=True
        )

        if serializer.is_valid():
            logger.info("Valid data: %s", serializer.validated_data)
            serializer.save()
            return response.Response(data=serializer.data, status=status.HTTP_200_OK)
        else:
            logger.error("Invalid data: %s", serializer.errors)
            return response.Response(
                data=serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

    def destroy(self, request, pk=None, *args, **kwargs) -> response.Response:
        instance = self.get_object()
        if self.request.user == instance.user_id:
            super(TaskViewSet, self).destroy(request, pk, *args, **kwargs)
            return response.Response(
                data="Task was successfully deleted", status=status.HTTP_204_NO_CONTENT
            )
        else:
            return response.Response(
                data="Permission to task was denied",
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )
