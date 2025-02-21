from django.db.models import Prefetch
from django.utils.functional import cached_property
from django.views.generic import DetailView, UpdateView
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from rules.contrib.views import PermissionRequiredMixin
from view_breadcrumbs import (
    DetailBreadcrumbMixin,
    ListBreadcrumbMixin,
    UpdateBreadcrumbMixin,
)

from .filters import ProjectFilter
from .forms import ProjectForm
from .models import Project, ProjectsConfiguration
from .tables import ProjectTable


class ProjectListView(
    PermissionRequiredMixin, ListBreadcrumbMixin, SingleTableMixin, FilterView
):
    model = Project
    table_class = ProjectTable
    filterset_class = ProjectFilter
    permission_required = "projects.view_project"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("category", "section")
            .prefetch_related("topics")
        )


class ProjectDetailView(PermissionRequiredMixin, DetailBreadcrumbMixin, DetailView):
    model = Project
    permission_required = "projects.view_project"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("category", "section")
            .prefetch_related("topics", Prefetch("members__user"))
        )


class ProjectUpdate(PermissionRequiredMixin, UpdateBreadcrumbMixin, UpdateView):
    permission_required = "projects.change_project"
    model = Project
    form_class = ProjectForm


class ProjectDMPView(PermissionRequiredMixin, DetailBreadcrumbMixin, DetailView):
    model = Project
    permission_required = "projects.change_project"
    template_name_suffix = "_detail_dmp"

    @cached_property
    def crumbs(self):
        return super().crumbs + [("DMP", "")]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["projects_config"] = ProjectsConfiguration.get_solo()
        return ctx
