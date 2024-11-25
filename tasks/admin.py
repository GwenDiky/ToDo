from django.contrib import admin

from tasks.models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "deadline", "is_notified")
    list_filter = ("status", "is_notified")
    search_fields = ("title", "description")