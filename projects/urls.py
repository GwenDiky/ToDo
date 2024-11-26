from projects.viewsets import ProjectViewSet
from rest_framework.routers import DefaultRouter

app_name = "projects"

router = DefaultRouter()
router.register(r"projects", ProjectViewSet)

urlpatterns = router.urls
