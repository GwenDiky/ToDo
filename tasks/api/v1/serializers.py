from rest_framework import serializers

from projects.models import Project
from tasks.models import Task


class TaskSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(), required=False
    )
    user_id = serializers.IntegerField(required=False, write_only=True)

    class Meta:
        model = Task
        fields = [
            "title",
            "body",
            "status",
            "deadline",
            "notification",
            "project",
            "user_id",
        ]

    def create(self, validated_data):
        project = validated_data.pop("project", None)
        task = Task.objects.create(**validated_data, project=project)
        return task
