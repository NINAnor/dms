from django.views.generic import DetailView
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from rules.contrib.views import PermissionRequiredMixin
from view_breadcrumbs import DetailBreadcrumbMixin, ListBreadcrumbMixin

from .filters import ResourceFilter, ServiceFilter
from .models import Resource, Service
from .tables import ContributorTable, ResourceTable, ServiceResourceTable, ServiceTable


class ServiceListView(
    PermissionRequiredMixin, ListBreadcrumbMixin, SingleTableMixin, FilterView
):
    model = Service
    table_class = ServiceTable
    filterset_class = ServiceFilter
    permission_required = "services.view_service"


class ServiceDetailView(PermissionRequiredMixin, DetailBreadcrumbMixin, DetailView):
    model = Service
    permission_required = "services.view_service"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["resource_table"] = ResourceTable(self.object.resources.all())
        ctx["contributor_table"] = ContributorTable(self.object.contributors.all())
        return ctx


class ServiceResourceListView(
    PermissionRequiredMixin, ListBreadcrumbMixin, SingleTableMixin, FilterView
):
    model = Resource
    table_class = ServiceResourceTable
    filterset_class = ResourceFilter
    permission_required = "services.view_resource"
