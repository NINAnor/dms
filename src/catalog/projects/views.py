from django.views.generic import DetailView, UpdateView
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from rules.contrib.views import PermissionRequiredMixin
from view_breadcrumbs import (
    DetailBreadcrumbMixin,
    ListBreadcrumbMixin,
)

from .filters import ProjectFilter
from .forms import ProjectForm
from .models import Project
from .tables import ProjectTable


class ProjectListView(
    PermissionRequiredMixin, ListBreadcrumbMixin, SingleTableMixin, FilterView
):
    model = Project
    table_class = ProjectTable
    filterset_class = ProjectFilter
    permission_required = "projects.read_project"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("category", "section")
            .prefetch_related("topics")
        )


class ProjectDetailView(PermissionRequiredMixin, DetailBreadcrumbMixin, DetailView):
    model = Project
    permission_required = "projects.read_project"


class ProjectUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = "projects.change_project"
    model = Project
    form_class = ProjectForm
