from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from rules.contrib.views import PermissionRequiredMixin
from view_breadcrumbs import ListBreadcrumbMixin

from .filters import ServiceFilter
from .models import Service
from .tables import ServiceTable


class ServiceListView(
    PermissionRequiredMixin, ListBreadcrumbMixin, SingleTableMixin, FilterView
):
    model = Service
    table_class = ServiceTable
    filterset_class = ServiceFilter
    permission_required = "services.view_services"
