from rest_framework.routers import DefaultRouter

from projects.viewsets import ProjectViewSet

app_name = "projects"

router = DefaultRouter()
router.register(r"projects", ProjectViewSet)

urlpatterns = router.urls
