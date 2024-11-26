from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny
from rest_framework.routers import DefaultRouter

from projects.urls import router as projects_router
from tasks.urls import router as tasks_router

swagger_view = get_schema_view(
    openapi.Info(
        title="Tasks API",
        default_version="v1",
        description="API for tasks & projects",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@tasks.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(AllowAny,),
    authentication_classes=[],
)

main_router = DefaultRouter()
main_router.registry.extend(tasks_router.registry)
main_router.registry.extend(projects_router.registry)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(main_router.urls)),
    path(
        "swagger/",
        swagger_view.with_ui("swagger", cache_timeout=0),
        name="swagger-docs",
    ),
]
