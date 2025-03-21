from django.urls import path

from ..projects import views

app_name = "projects"

urlpatterns = [
    path("projects/", views.ProjectListView.as_view(), name="project_list"),
    path(
        "projects/<int:pk>/", views.ProjectDetailView.as_view(), name="project_detail"
    ),
    path(
        "projects/<int:pk>/update/",
        views.ProjectUpdateView.as_view(),
        name="project_update",
    ),
    path("dmps/", views.DMPListView.as_view(), name="dmp_list"),
    path("dmps/create/", views.DMPCreateView.as_view(), name="dmp_create"),
    path("dmps/<int:pk>/", views.DMPDetailView.as_view(), name="dmp_detail"),
    path("dmps/<int:pk>/edit/", views.DMPUpdateView.as_view(), name="dmp_update"),
    path(
        "dmps/<int:pk>/edit/data/",
        views.DMPSurveyView.as_view(),
        name="dmp_edit_survey",
    ),
]
