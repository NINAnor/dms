from django.urls import path

from ..datasets import views

app_name = "datasets"

urlpatterns = [
    path("datasets/", views.DatasetListView.as_view(), name="dataset_list"),
    path("resources/", views.ResourceListView.as_view(), name="resource_list"),
    path(
        "datasets/register/", views.DatasetCreateView.as_view(), name="dataset_create"
    ),
    path(
        "datasets/<str:pk>/", views.DatasetDetailView.as_view(), name="dataset_detail"
    ),
    # Dataset Relationships
    path(
        "datasets/<str:pk>/relationships/",
        views.DatasetRelationshipListView.as_view(),
        name="dataset_relationship_list",
    ),
    # Dataset Contributions
    path(
        "datasets/<str:dataset_pk>/contributions/edit/",
        views.DatasetContributionManageView.as_view(),
        name="dataset_contribution_manage",
    ),
    path(
        "datasets/<str:dataset_pk>/contributions/create/",
        views.DatasetContributionCreateView.as_view(),
        name="dataset_contribution_create",
    ),
    path(
        "datasets/<str:dataset_pk>/contributions/edit/<int:user_pk>/",
        views.DatasetContributionUpdateView.as_view(),
        name="dataset_contribution_update",
    ),
    path(
        "datasets/<str:dataset_pk>/contributions/delete/<int:user_pk>/",
        views.DatasetContributionDeleteView.as_view(),
        name="dataset_contribution_delete",
    ),
    # Dataset
    path(
        "datasets/<str:pk>/edit/",
        views.DatasetUpdateView.as_view(),
        name="dataset_update",
    ),
    path(
        "datasets/<str:pk>/edit/metadata/",
        views.DatasetUpdateMetadataView.as_view(),
        name="dataset_update_metadata",
    ),
    path(
        "datasets/<str:pk>/delete/",
        views.DatasetDeleteView.as_view(),
        name="dataset_delete",
    ),
    path(
        "datasets/<str:pk>/clone/",
        views.DatasetCloneView.as_view(),
        name="dataset_clone",
    ),
    # Resources
    path(
        "datasets/<str:dataset_pk>/resources/register/",
        views.ResourceCreateView.as_view(),
        name="resource_create",
    ),
    path(
        "datasets/<str:dataset_pk>/resources/<str:pk>/",
        views.ResourceDetailView.as_view(),
        name="resource_detail",
    ),
    path(
        "datasets/<str:dataset_pk>/resources/<str:pk>/edit/",
        views.ResourceUpdateView.as_view(),
        name="resource_update",
    ),
    path(
        "datasets/<str:dataset_pk>/resources/<str:pk>/delete/",
        views.ResourceDeleteView.as_view(),
        name="resource_delete",
    ),
    path(
        "datasets/<str:dataset_pk>/resources/<str:pk>/refresh-metadata/",
        views.ResourceRefreshMetadataView.as_view(),
        name="resource_refresh_metadata",
    ),
    # Type-specific resource URLs
    path(
        "datasets/<str:dataset_pk>/resources/map/register/",
        views.MapResourceCreateView.as_view(),
        name="mapresource_create",
    ),
    path(
        "datasets/<str:dataset_pk>/resources/map/<str:pk>/edit/",
        views.MapResourceUpdateView.as_view(),
        name="mapresource_update",
    ),
    path(
        "datasets/<str:dataset_pk>/resources/raster/register/",
        views.RasterResourceCreateView.as_view(),
        name="rasterresource_create",
    ),
    path(
        "datasets/<str:dataset_pk>/resources/raster/<str:pk>/edit/",
        views.RasterResourceUpdateView.as_view(),
        name="rasterresource_update",
    ),
    path(
        "datasets/<str:dataset_pk>/resources/tabular/register/",
        views.TabularResourceCreateView.as_view(),
        name="tabularresource_create",
    ),
    path(
        "datasets/<str:dataset_pk>/resources/tabular/<str:pk>/edit/",
        views.TabularResourceUpdateView.as_view(),
        name="tabularresource_update",
    ),
    path(
        "datasets/<str:dataset_pk>/resources/partitioned/register/",
        views.PartitionedResourceCreateView.as_view(),
        name="partitionedresource_create",
    ),
    path(
        "datasets/<str:dataset_pk>/resources/partitioned/<str:pk>/edit/",
        views.PartitionedResourceUpdateView.as_view(),
        name="partitionedresource_update",
    ),
]
