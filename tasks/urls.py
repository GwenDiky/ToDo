from rest_framework.routers import DefaultRouter

from tasks.viewsets import TaskViewSet

app_name = "tasks"

router = DefaultRouter()
router.register(r"tasks", TaskViewSet)

urlpatterns = router.urls
