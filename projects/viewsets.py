from rest_framework import viewsets
from projects.models import Project
from projects.api.v1 import serializers
from projects.api.v1.filters import ProjectFilter
from todo.mixins import FileEventMixin
from todo.api.v1.kafka_event_sender import KafkaEventSender

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().order_by("-pk")
    serializer_class = serializers.ProjectSerializer
    lookup_field = "id"

    filter_backends = (DjangoFilterBackend, drf_filters.OrderingFilter)
    filterset_class = ProjectFilter
    ordering_fields = ["title", "created_at"]

    authentication_classes = [JWTAuthenticationCustom]
    permission_classes = [IsAuthenticatedById]

    def get_queryset(self):
        return Project.objects.filter(
            tasks__user_id=self.request.user
        ).distinct()

    def perform_create(self, serializer):
        project = serializer.save()
        self.send_file_event(event_type="upload_file", instance=project)
        return project

    def perform_update(self, serializer):
        project = self.get_object()
        previous_attachment = project.attachment_url
        updated_project = serializer.save()

        if previous_attachment != updated_project.attachment_url:
            self.send_file_event(
                event_type="update_file", instance=updated_project
            )

        return updated_project

    def perform_destroy(self, instance):
        if instance.attachment_url:
            self.send_file_event(event_type="delete_file", instance=instance)
        super().perform_destroy(instance)

    def send_file_event(self, event_type, project):
        if project.attachment_url:
            file_name, file_type = extract_file_info(project.attachment_url)
            file_instance = {
                "file_name": file_name,
                "file_type": file_type,
                "file_url": project.attachment_url,
            }
            KafkaEventSender.send_attachment_event(
                event_type=event_type, instance=file_instance
            )
            logger.info(f"Sent event '{event_type}' for file {project.attachment_url}")
