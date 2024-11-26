from tasks.viewsets import TaskViewSet
from rest_framework.routers import DefaultRouter
from django.urls import include, path
from rest_framework.decorators import api_view

app_name = "tasks"

router = DefaultRouter()
router.register(r"tasks", TaskViewSet)

urlpatterns = router.urls
