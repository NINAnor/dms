# from django.db.models import Prefetch
# from django.urls import reverse_lazy
from django.urls import reverse
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

from .filters import DatasetFilter
from .forms import DatasetForm, DatasetMetadataForm, DatasetUpdateForm
from .models import Dataset
from .tables import DatasetTable


class DatasetListView(
    PermissionRequiredMixin, ListBreadcrumbMixin, SingleTableMixin, FilterView
):
    model = Dataset
    table_class = DatasetTable
    filterset_class = DatasetFilter
    permission_required = "datasets.view_dataset"

    def get_queryset(self):
        return super().get_queryset()


class DatasetDetailView(PermissionRequiredMixin, DetailBreadcrumbMixin, DetailView):
    model = Dataset
    permission_required = "datasets.view_dataset"


class DatasetCreateView(PermissionRequiredMixin, CreateBreadcrumbMixin, CreateView):
    permission_required = "datasets.add_dataset"
    model = Dataset
    form_class = DatasetForm

    def get_success_url(self):
        return reverse(
            "datasets:dataset_update_metadata", kwargs={"pk": self.object.pk}
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        if project_id := self.request.GET.get("project"):
            initial["project"] = project_id
        return initial


class DatasetUpdateView(PermissionRequiredMixin, UpdateBreadcrumbMixin, UpdateView):
    permission_required = "datasets.change_dataset"
    model = Dataset
    form_class = DatasetUpdateForm


class DatasetUpdateMetadataView(
    PermissionRequiredMixin, UpdateBreadcrumbMixin, UpdateView
):
    permission_required = "datasets.change_dataset"
    model = Dataset
    form_class = DatasetMetadataForm

    def form_invalid(self, form):
        print(self.request.POST)
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse("datasets:dataset_detail", kwargs={"pk": self.object.pk})
