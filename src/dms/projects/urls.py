from django.urls import path

from ..projects import views

app_name = "projects"

urlpatterns = [
    path("projects/", views.ProjectListView.as_view(), name="project_list"),
    path(
        "projects/<str:pk>/", views.ProjectDetailView.as_view(), name="project_detail"
    ),
    path(
        "projects/<str:pk>/update/",
        views.ProjectUpdateView.as_view(),
        name="project_update",
    ),
    path("dmps/", views.DMPListView.as_view(), name="dmp_list"),
    path("dmps/personal/", views.MyDMPListView.as_view(), name="dmp_list-personal"),
    path("dmps/create/", views.DMPCreateView.as_view(), name="dmp_create"),
    path("dmps/<int:pk>/", views.DMPDetailView.as_view(), name="dmp_detail"),
    path("dmps/<int:pk>/preview/", views.DMPPreviewView.as_view(), name="dmp_preview"),
    path("dmps/<int:pk>/edit/", views.DMPUpdateView.as_view(), name="dmp_update"),
    path("dmps/<int:pk>/delete/", views.DMPDeleteView.as_view(), name="dmp_delete"),
    path(
        "projects/<str:project_pk>/membership/edit/",
        views.ProjectMembershipManageView.as_view(),
        name="project_membership_manage",
    ),
    path(
        "projects/<str:project_pk>/membership/create/",
        views.ProjectMembershipCreateView.as_view(),
        name="project_membership_create",
    ),
    path(
        "projects/<str:project_pk>/membership/edit/<int:user_pk>/",
        views.ProjectMembershipUpdateView.as_view(),
        name="project_membership_update",
    ),
    path(
        "projects/<str:project_pk>/membership/delete/<int:user_pk>/",
        views.ProjectMembershipDeleteView.as_view(),
        name="project_membership_delete",
    ),
]
