from django.urls import path

from .views import ProjectDetailView, ProjectDMPView, ProjectListView, ProjectUpdate

app_name = "projects"

urlpatterns = [
    path("projects/", ProjectListView.as_view(), name="project_list"),
    path("projects/<int:pk>/", ProjectDetailView.as_view(), name="project_detail"),
    path("projects/<int:pk>/update/", ProjectUpdate.as_view(), name="project_update"),
    path("projects/<int:pk>/dmp/", ProjectDMPView.as_view(), name="project_dmp"),
]
