import logging
import os
from uuid import uuid4
import jwt
from asgiref.sync import async_to_sync
from django.core.mail import send_mail
from django.shortcuts import render, redirect, reverse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (viewsets, status, exceptions, permissions,
                            response, authentication, filters as drf_filters)
from tasks.api.v1 import serializers, utils, filters
from tasks.models import Task
from todo.viewsets import (StandardPaginationViewSet, IsAuthenticatedById,
                           JWTAuthenticationCustom)
from django.db.models.query import QuerySet
from rest_framework.exceptions import NotAuthenticated

logger = logging.getLogger(__name__)

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all().order_by("-created_at")

    serializer_class = serializers.TaskSerializer

    filter_backends = (DjangoFilterBackend,
                       drf_filters.OrderingFilter)

    filterset_class = filters.FilterTasks
    ordering = ["created_at"]
    pagination_class = StandardPaginationViewSet
    ordering_fields = ["title", "created_at"]

    authentication_classes = [JWTAuthenticationCustom]
    permission_classes = [IsAuthenticatedById]

    def get_queryset(self) -> QuerySet[Task]:
        if self.request.user.is_authenticated:
            user_id = self.request.user
        else: raise NotAuthenticated("User is not authenticated.")
        return Task.objects.filter(user_id=user_id)

    def retrieve(self, request, pk=None) -> response.Response:
        instance = self.get_object()
        return response.Response(self.serializer_class(instance).data,
                        status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs) -> response.Response:
        user = request.user
        data = request.data
        data.update({"user_id": user})
        logger.info(f"id of current user: {user}")
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save()
            return response.Response(data=serializer.data,
                            status=status.HTTP_201_CREATED)
        else:
            return response.Response(data=serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    def perform_update(self, request, pk=None, *args, **kwargs) -> (
            response.Response):
        user = self.request.user
        instance = self.get_object()
        data = {"title": request.data.get('title', None),
                "body": request.data.get('body', None),
                "status": request.data.get('status', None),
                "project": request.data.get('project', None),
                "deadline": request.data.get('deadline', None),
                "notification": request.data.get("notification", None)}
        logger.info(
            f"Change task with the title {data['title']}"
        )

        if request.data.get('status'):
            logger.info(f"Status of task {instance.title} was changed.")


        if (instance.notification and request.data.get('status') !=
                instance.status):
            mail_of_recipient = async_to_sync(utils.get_email_of_user)(user)
            mail = mail.Mail(
                recipient=mail_of_recipient,
                subject="Status of task changed. Hurry up!",
                body=f"Hello. The status of task {data['title']} changed to {data['status']}.",
            )

            logger.info(f"Working with the task: {data['title']}")
            async_to_sync(mail.send_email_notification)(title_of_task=data[
                'title'])

        serializer = self.serializer_class(instance=instance,
                                           data=data,
                                           context={'author': user},
                                           partial=True)
        if serializer.is_valid():
            serializer.save()
            return response.Response(data=serializer.data,
                            status=status.HTTP_201_CREATED)
        else:
            return response.Response(data=serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None, *args, **kwargs) -> response.Response:
        instance = self.get_object()
        if self.request.user == instance.user_id:
            super(TaskViewSet, self).destroy(request, pk, *args,
                                                       **kwargs)
            return response.Response(data="Task was successfully deleted",
                            status=status.HTTP_204_NO_CONTENT)
        else:
            return response.Response(
                data="Permission to task was denied",
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
