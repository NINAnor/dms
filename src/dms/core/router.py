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
router.register("resources", datasets_views.ResourceViewSet, basename="resources")
router.register(
    "mapresources", datasets_views.MapResourceViewSet, basename="mapresources"
)
router.register(
    "rasterresources", datasets_views.RasterResourceViewSet, basename="rasterresources"
)
router.register(
    "tabularresources",
    datasets_views.TabularResourceViewSet,
    basename="tabularresources",
)
router.register(
    "partitionedresources",
    datasets_views.PartitionedResourceViewSet,
    basename="partitionedresources",
)
router.register(
    "datasets-relationships",
    datasets_views.DatasetRelationshipViewSet,
    basename="dataset-relationships",
)
router.register("datatables", datasets_views.DataTableViewSet, basename="datatables")

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
