from __future__ import absolute_import, unicode_literals
from tasks.api.v1.celery import app as celery_app

__all__ = ("celery_app",)
