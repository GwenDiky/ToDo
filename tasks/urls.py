from tasks.viewsets import TaskViewSet
from rest_framework.routers import DefaultRouter

app_name = "tasks"

router = DefaultRouter()
router.register(r"tasks", TaskViewSet)

urlpatterns = router.urls