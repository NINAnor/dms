from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework_nested import routers

from catalog.projects.api import views as projects_views

router = routers.DefaultRouter()
router.register("projects", projects_views.ProjectModelViewSet, basename="projects")

app_name = "api_v1"

urlpatterns = [
    path("auth/", include("dj_rest_auth.urls")),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("docs/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
] + router.urls
