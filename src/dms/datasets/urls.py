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
]
