from django.db import models


class StatusChoices(models.TextChoices):
    DONE = 'done', 'Done'
    IN_PROGRESS = 'in_progress', 'In Progress'
    TO_DO = 'to_do', 'To Do'
