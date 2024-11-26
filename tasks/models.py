from django.db import models

from projects.models import Project
from tasks.api.v1.validators import validate_user_exists


class Task(models.Model):
    STATUS_CHOICES = {"done": "Done", "in_progress": "In Progress", "to_do": "To Do"}
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True, null=True)

    status = models.CharField(choices=STATUS_CHOICES, max_length=50, default="done")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    deadline = models.DateTimeField(blank=True)

    user_id = models.IntegerField(
        blank=True, null=True, validators=[validate_user_exists]
    )

    notification = models.BooleanField(
        "Do you need to be notified of deadlines?", default=True
    )
    is_notified = models.BooleanField(default=False)

    subscription = models.BooleanField(
        "Do u need to be notified of status changes", default=True
    )

    def __str__(self):
        return str(self.title) if self.title else "Untitled Task"
