from django.urls import path

from ..datasets import views

app_name = "datasets"

urlpatterns = [
    path("datasets/", views.DatasetListView.as_view(), name="dataset_list"),
    path(
        "datasets/register/", views.DatasetCreateView.as_view(), name="dataset_create"
    ),
    path(
        "datasets/<str:pk>/", views.DatasetDetailView.as_view(), name="dataset_detail"
    ),
    path(
        "datasets/<str:pk>/relationships/",
        views.DatasetRelationshipListView.as_view(),
        name="dataset_relationship_list",
    ),
    path(
        "datasets/<str:dataset_pk>/relationships/edit/",
        views.DatasetRelationshipManageView.as_view(),
        name="dataset_relationship_manage",
    ),
    path(
        "datasets/<str:dataset_pk>/relationships/create/",
        views.DatasetRelationshipCreateView.as_view(),
        name="dataset_relationship_create",
    ),
    path(
        "datasets/<str:dataset_pk>/relationships/edit/<str:pk>/",
        views.DatasetRelationshipUpdateView.as_view(),
        name="dataset_relationship_update",
    ),
    path(
        "datasets/<str:dataset_pk>/relationships/delete/<str:pk>/",
        views.DatasetRelationshipDeleteView.as_view(),
        name="dataset_relationship_delete",
    ),
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
        "datasets/<str:dataset_pk>/resources/<str:pk>/edit/metadata/",
        views.ResourceMetadataUpdateView.as_view(),
        name="resource_update_metadata",
    ),
]
