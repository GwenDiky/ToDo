from django.db import models

from projects.models import Project
from tasks.api.v1.validators import validate_user_exists
from tasks.enums import STATUS_CHOICES
from todo.models import BaseModelFieldsMixin


class Task(BaseModelFieldsMixin):
    body = models.TextField(blank=True, null=True)

    status = models.CharField(
        choices=STATUS_CHOICES, max_length=50, default="done"
    )
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="tasks"
    )
    deadline = models.DateTimeField(blank=True)

    user_id = models.IntegerField(
        blank=True, null=True, validators=[validate_user_exists]
    )

    is_subscribed_deadlines = models.BooleanField(
        "Do you need to be notified of deadlines?", default=True
    )
    is_notified = models.BooleanField(default=False)
    is_subscribed_status_changing = models.BooleanField(
        "Do u need to be notified of status changes", default=True
    )

    def __str__(self):
        return self.title
