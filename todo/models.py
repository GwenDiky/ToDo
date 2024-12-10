from django.db import models


class BaseModelFieldsMixin(models.Model):
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    attachment_url = models.CharField(
        "Static's URL", max_length=255, blank=True, null=True
    )


    class Meta:
        abstract = True
