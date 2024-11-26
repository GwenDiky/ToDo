from rest_framework.routers import DefaultRouter

from tasks.viewsets import TaskViewSet

APP_NAME = "tasks"

router = DefaultRouter()
router.register(r"tasks", TaskViewSet)

urlpatterns = router.urls
