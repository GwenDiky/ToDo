from rest_framework import serializers

from projects.models import Project
from tasks.api.v1.validators import validate_user_exists
from tasks.models import Task


class TaskSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(), required=False
    )
    user_id = serializers.IntegerField(
        required=False, write_only=True, validators=[validate_user_exists]
    )

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "body",
            "status",
            "deadline",
            "is_subscribed_deadlines",
            "is_subscribed_status_changing",
            "project",
            "user_id",
        ]

    def create(self, validated_data):
        project = validated_data.pop("project", None)
        task = Task.objects.create(**validated_data, project=project)
        return task
