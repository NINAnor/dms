from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework_nested import routers

from dms.datasets.api import views as datasets_views
from dms.projects.api import views as projects_views

router = routers.DefaultRouter()
router.register("projects", projects_views.ProjectModelViewSet, basename="projects")
router.register("dmps", projects_views.DMPModelViewSet, basename="dmps")
router.register("datasets", datasets_views.DatasetViewSet, basename="datasets")
router.register("storages", datasets_views.StorageViewSet, basename="storages")
router.register("resources", datasets_views.ResourceViewSet, basename="resources")
router.register(
    "datasets-relationships",
    datasets_views.DatasetRelationshipViewSet,
    basename="dataset-relationships",
)

app_name = "api_v1"

urlpatterns = [
    path("auth/", include("dj_rest_auth.urls")),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "docs/",
        SpectacularSwaggerView.as_view(url_name="api_v1:schema"),
        name="swagger-ui",
    ),
    path(
        "docs/redoc/",
        SpectacularRedocView.as_view(url_name="api_v1:schema"),
        name="redoc",
    ),
] + router.urls
