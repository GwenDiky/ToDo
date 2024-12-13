# tasks/api/v1/views.py
from rest_framework import viewsets
from tasks.models import Task
from tasks.api.v1 import serializers
from todo.mixins import (TaskCreateMixin, TaskUpdateMixin,
                             TaskDestroyMixin, TaskListMixin)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters as drf_filters

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
