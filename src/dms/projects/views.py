from django.db.models import Prefetch
from django.utils.functional import cached_property
from django.views.generic import CreateView, DetailView, UpdateView
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from rules.contrib.views import PermissionRequiredMixin
from view_breadcrumbs import (
    CreateBreadcrumbMixin,
    DetailBreadcrumbMixin,
    ListBreadcrumbMixin,
    UpdateBreadcrumbMixin,
)

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
            .prefetch_related("tags", Prefetch("members__user"))
        )


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

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return super().get_queryset()
        return super().get_queryset().none()


class DMPCreateView(PermissionRequiredMixin, CreateBreadcrumbMixin, CreateView):
    permission_required = "projects.add_dmp"
    model = DMP
    form_class = DMPForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class DMPUpdateView(PermissionRequiredMixin, UpdateBreadcrumbMixin, UpdateView):
    permission_required = "projects.change_dmp"
    model = DMP
    form_class = DMPForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class DMPSurveyView(PermissionRequiredMixin, DetailBreadcrumbMixin, DetailView):
    model = DMP
    permission_required = "projects.change_dmp"
    template_name_suffix = "_edit_json"

    @cached_property
    def crumbs(self):
        return super().crumbs + [("DMP", "")]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["projects_config"] = ProjectsConfiguration.get_solo()
        return ctx
