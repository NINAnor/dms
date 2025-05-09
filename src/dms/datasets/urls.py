from django.urls import path

from ..datasets import views

app_name = "datasets"

urlpatterns = [
    path("datasets/", views.DatasetListView.as_view(), name="dataset_list"),
    path(
        "datasets/register/", views.DatasetCreateView.as_view(), name="dataset_create"
    ),
    path(
        "datasets/<uuid:pk>/", views.DatasetDetailView.as_view(), name="dataset_detail"
    ),
    path(
        "datasets/<uuid:pk>/relationships/",
        views.DatasetRelationshipListView.as_view(),
        name="dataset_relationship_list",
    ),
    path(
        "datasets/<uuid:dataset_pk>/relationships/edit/",
        views.DatasetRelationshipManageView.as_view(),
        name="dataset_relationship_manage",
    ),
    path(
        "datasets/<uuid:dataset_pk>/relationships/create/",
        views.DatasetRelationshipCreateView.as_view(),
        name="dataset_relationship_create",
    ),
    path(
        "datasets/<uuid:dataset_pk>/relationships/edit/<uuid:pk>/",
        views.DatasetRelationshipUpdateView.as_view(),
        name="dataset_relationship_update",
    ),
    path(
        "datasets/<uuid:dataset_pk>/relationships/delete/<uuid:pk>/",
        views.DatasetRelationshipDeleteView.as_view(),
        name="dataset_relationship_delete",
    ),
    path(
        "datasets/<uuid:pk>/edit/",
        views.DatasetUpdateView.as_view(),
        name="dataset_update",
    ),
    path(
        "datasets/<uuid:pk>/edit/metadata/",
        views.DatasetUpdateMetadataView.as_view(),
        name="dataset_update_metadata",
    ),
    path(
        "datasets/<uuid:dataset_pk>/resources/register/",
        views.ResourceCreateView.as_view(),
        name="resource_create",
    ),
    path(
        "datasets/<uuid:dataset_pk>/resources/<uuid:pk>/",
        views.ResourceDetailView.as_view(),
        name="resource_detail",
    ),
    path(
        "datasets/<uuid:dataset_pk>/resources/<uuid:pk>/edit/",
        views.ResourceUpdateView.as_view(),
        name="resource_update",
    ),
    path(
        "datasets/<uuid:dataset_pk>/resources/<uuid:pk>/infer-schema/",
        views.ResourceInferSchemaView.as_view(),
        name="resource_infer_schema",
    ),
    path(
        "datasets/<uuid:dataset_pk>/resources/<uuid:pk>/edit/metadata/",
        views.ResourceMetadataUpdateView.as_view(),
        name="resource_update_metadata",
    ),
    path("storages/", views.StorageListView.as_view(), name="storage_list"),
    path(
        "storages/register/", views.StorageCreateView.as_view(), name="storage_create"
    ),
    path(
        "storages/<uuid:pk>/edit/",
        views.StorageUpdateView.as_view(),
        name="storage_update",
    ),
    path(
        "storages/<uuid:pk>/config/",
        views.StorageConfigView.as_view(),
        name="storage_update_config",
    ),
    path(
        "storages/<uuid:pk>/", views.StorageDetailView.as_view(), name="storage_detail"
    ),
    path(
        "options/resource-type/",
        views.ResourceMediaTypeOptionsView.as_view(),
        name="resource_type_list",
    ),
]
