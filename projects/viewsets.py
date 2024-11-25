from django.shortcuts import render
from projects.models import Project
from todo.viewsets import StandardPaginationViewSet
from rest_framework import viewsets
from projects.api.v1 import serializers

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().order_by("-created_at")
    serializer_class = serializers.ProjectSerializer
    lookup_field = "id"
    pagination_class = StandardPaginationViewSet