import requests
from django.conf import settings
from django.db.models import F, Prefetch
from django.http import HttpResponse
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

from dms.datasets.tables import DatasetTable
from dms.services.tables import ServiceTable

from .filters import DMPFilter, ProjectFilter
from .forms import DMPForm, ProjectForm
from .libs.render_latex import render_to_tex
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
        ctx["services"] = ServiceTable(self.object.services.all(), prefix="services-")
        ctx["datasets"] = DatasetTable(self.object.datasets.all(), prefix="datasets-")
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
        return (
            super()
            .get_queryset()
            .order_by(F("featured_at").desc(nulls_last=True), "-updated_at")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "DMPs"
        return ctx


class MyDMPListView(
    PermissionRequiredMixin, ListBreadcrumbMixin, SingleTableMixin, FilterView
):
    model = DMP
    table_class = DMPTable
    filterset_class = DMPFilter
    permission_required = "projects.view_dmp"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "My DMPs"
        return ctx

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


class DMPPreviewView(PermissionRequiredMixin, DetailView):
    model = DMP
    permission_required = "projects.view_dmp"

    formats = {
        "html": {"content_type": "text/html", "ext": "html"},
        "latex": {"content_type": "text/plain", "ext": "tex"},
        "pdf": {"content_type": "application/pdf", "ext": "pdf"},
        "docx": {"content_type": "application/vnd.openxmlformats", "ext": "docx"},
    }

    def render_to_response(self, context, **response_kwargs):
        # Get format from query parameter, default to html
        format_param = self.request.GET.get("format", "html").lower()

        # Validate format parameter
        if format_param not in self.formats.keys():
            selected_format = self.formats["html"]
            format_param = "html"
        else:
            selected_format = self.formats[format_param]

        conf = ProjectsConfiguration.objects.select_related("dmp_survey_config").first()

        latex_content = render_to_tex(conf.dmp_survey_config.config, self.object.data)
        if format_param == "latex":
            return latex_content

        response = requests.post(
            settings.FASTDOC_CONVERT_API_URL,
            json={
                "text": latex_content,
                "input_format": "latex",
                "output_format": format_param,
            },
            timeout=20,
        )
        # NOTE: timeout is not handled intentionally
        # TODO: move this in queue and save the outputs to s3

        # Set filename for download
        filename = f"dmp_{self.object.name}.{selected_format['ext']}"

        response = HttpResponse(
            response.content, content_type=response.headers["Content-Type"]
        )
        if format_param != "html":
            response["Content-Disposition"] = f'attachment; filename="{filename}"'

        return response


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
