from datetime import datetime

from rest_framework import serializers

from projects.api.v1.serializers import ProjectSerializer
from projects.models import Project
from tasks.api.v1.validators import validate_user_exists
from tasks.enums import STATUS_CHOICES
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
        fields = "__all__"


class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        exclude = ["id", "is_notified", "created_at", "updated_at"]

    def validate_status(self, attrs):
        if attrs.get("status") not in STATUS_CHOICES:
            raise serializers.ValidationError("Invalid priority value.")
        return attrs

    def validate_body(self, value):
        if len(value) < 10:
            raise serializers.ValidationError(
                "Body must be at least 10 characters long."
            )
        return value

    def validate_deadline(self, value):
        if value and value < datetime.now():
            raise serializers.ValidationError(
                "Deadline cannot be in the past."
            )
        return value


class TaskListSerializer(serializers.ModelSerializer):
    project = ProjectSerializer(read_only=True)

    class Meta:
        model = Task
        fields = ["id", "title", "status", "created_at", "deadline", "project"]


class TaskUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            "title",
            "body",
            "status",
            "deadline",
            "is_subscribed_deadlines",
            "is_notified",
            "is_subscribed_status_changing",
            "user_id",
        ]
        extra_kwargs = {
            "status": {"required": False},
        }
