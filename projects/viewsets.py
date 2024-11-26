from django.db.models.query import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters as drf_filters
from rest_framework import viewsets
from rest_framework.exceptions import NotAuthenticated

from projects.api.v1 import filters
from projects.models import Project
from tasks.api.v1 import serializers
from todo.jwt_auth import IsAuthenticatedById, JWTAuthenticationCustom
from todo.viewsets import StandardPaginationViewSet


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().order_by("-created_at")
    serializer_class = serializers.ProjectSerializer
    lookup_field = "id"
    pagination_class = StandardPaginationViewSet

    filter_backends = (DjangoFilterBackend, drf_filters.OrderingFilter)

    filterset_class = filters.ProjectFilter
    ordering_fields = ["title", "created_at"]

    authentication_classes = [JWTAuthenticationCustom]
    permission_classes = [IsAuthenticatedById]

    def get_queryset(self) -> QuerySet[Project]:
        if self.request.user:
            user_id = self.request.user
        else:
            raise NotAuthenticated("User is not authenticated.")

        return Project.objects.filter(tasks__user_id=user_id).distinct()
