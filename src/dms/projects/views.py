from django.db.models import Prefetch
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from rules.contrib.views import PermissionRequiredMixin
from view_breadcrumbs import (
    CreateBreadcrumbMixin,
    DeleteBreadcrumbMixin,
    DetailBreadcrumbMixin,
    ListBreadcrumbMixin,
    UpdateBreadcrumbMixin,
)

from dms.services.tables import ServiceTable

from .filters import DMPFilter, ProjectFilter
from .forms import DMPForm, ProjectForm
from .models import DMP, Project, ProjectsConfiguration
from .tables import DMPTable, ProjectTable


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
            .prefetch_related("tags")
        )


class ProjectDetailView(PermissionRequiredMixin, DetailBreadcrumbMixin, DetailView):
    model = Project
    permission_required = "projects.view_project"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("category", "section")
            .prefetch_related("tags", Prefetch("members__user"), "services")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["services"] = ServiceTable(self.object.services.all())
        return ctx


class ProjectUpdateView(PermissionRequiredMixin, UpdateBreadcrumbMixin, UpdateView):
    permission_required = "projects.change_project"
    model = Project
    form_class = ProjectForm


class DMPListView(
    PermissionRequiredMixin, ListBreadcrumbMixin, SingleTableMixin, FilterView
):
    model = DMP
    table_class = DMPTable
    filterset_class = DMPFilter
    permission_required = "projects.view_dmp"

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return super().get_queryset().filter(owner=self.request.user)
        return super().get_queryset().none()


class DMPDetailView(PermissionRequiredMixin, DetailBreadcrumbMixin, DetailView):
    model = DMP
    permission_required = "projects.view_dmp"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["projects_config"] = ProjectsConfiguration.get_solo()
        return ctx


class DMPCreateView(PermissionRequiredMixin, CreateBreadcrumbMixin, CreateView):
    permission_required = "projects.add_dmp"
    model = DMP
    form_class = DMPForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        if project_id := self.request.GET.get("project"):
            initial["project"] = project_id
        return initial


class DMPUpdateView(PermissionRequiredMixin, UpdateBreadcrumbMixin, UpdateView):
    permission_required = "projects.change_dmp"
    model = DMP
    form_class = DMPForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class DMPDeleteView(PermissionRequiredMixin, DeleteBreadcrumbMixin, DeleteView):
    permission_required = "projects.delete_dmp"
    model = DMP
    success_url = reverse_lazy("projects:dmp_list")
