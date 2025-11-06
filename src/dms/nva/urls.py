from django.urls import path

from .views import DatasetPublicationLinkView, ProjectNVALinkView

app_name = "nva"

urlpatterns = [
    path(
        "projects/<str:pk>/nva-link/",
        ProjectNVALinkView.as_view(),
        name="project_nva_link",
    ),
    path(
        "datasets/<str:pk>/nva-publications/",
        DatasetPublicationLinkView.as_view(),
        name="dataset_publication_link",
    ),
]
