from rest_framework import serializers

from tasks.models import Task
from projects.models import Project


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ["id", "title"]

class TaskSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(), required=False
    )
    user_id = serializers.IntegerField(required=False, write_only=True)

    class Meta:
        model = Task
        fields = ['title', 'body', 'status', 'deadline', 'notification',
                  'project', 'user_id']

    def create(self, validated_data):
        project_data = validated_data.pop("project", None)
        if project_data is not None:
            task = Task.objects.create(**validated_data, project=project_data)
        else:
            task = Task.objects.create(**validated_data)

        return task
