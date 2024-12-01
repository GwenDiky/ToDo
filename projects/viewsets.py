from django.db.models.query import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters as drf_filters
from rest_framework import viewsets

from projects.api.v1 import filters, serializers
from projects.models import Project
from todo.jwt_auth import IsAuthenticatedById, JWTAuthenticationCustom
from todo.viewsets import StandardPaginationViewSet


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().order_by("-pk")
    serializer_class = serializers.ProjectSerializer
    lookup_field = "id"
    pagination_class = StandardPaginationViewSet

    filter_backends = (DjangoFilterBackend, drf_filters.OrderingFilter)

    filterset_class = filters.ProjectFilter
    ordering_fields = ["title", "created_at"]

    authentication_classes = [JWTAuthenticationCustom]
    permission_classes = [IsAuthenticatedById]

    def get_queryset(self) -> QuerySet[Project]:
        return Project.objects.filter(
            tasks__user_id=self.request.user
        ).distinct()
