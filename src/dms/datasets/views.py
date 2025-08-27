# from django.db.models import Prefetch
# from django.urls import reverse_lazy

from django.db.models import Q
from django.http import HttpResponse
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from rules.contrib.views import PermissionRequiredMixin
from view_breadcrumbs import (
    CreateBreadcrumbMixin,
    DetailBreadcrumbMixin,
    ListBreadcrumbMixin,
    UpdateBreadcrumbMixin,
)

from .filters import DatasetFilter, DatasetRelationshipFilter, ResourceFilter
from .forms import (
    DatasetForm,
    DatasetMetadataForm,
    DatasetRelationshipForm,
    DatasetUpdateForm,
    MapResourceForm,
    PartitionedResourceForm,
    RasterResourceForm,
    ResourceForm,
    TabularResourceForm,
)
from .models import (
    Dataset,
    DatasetRelationship,
    MapResource,
    PartitionedResource,
    RasterResource,
    Resource,
    TabularResource,
)
from .tables import DatasetRelationshipTable, DatasetTable, ResourceTable


class DatasetListView(
    PermissionRequiredMixin, ListBreadcrumbMixin, SingleTableMixin, FilterView
):
    model = Dataset
    table_class = DatasetTable
    filterset_class = DatasetFilter
    permission_required = "datasets.view_dataset"

    def get_queryset(self):
        return super().get_queryset()


class ResourceListView(
    PermissionRequiredMixin, ListBreadcrumbMixin, SingleTableMixin, FilterView
):
    model = Resource
    table_class = ResourceTable
    filterset_class = ResourceFilter
    permission_required = "datasets.view_resource"

    def get_queryset(self):
        return super().get_queryset().select_subclasses()


class DatasetDetailView(PermissionRequiredMixin, DetailBreadcrumbMixin, DetailView):
    model = Dataset
    permission_required = "datasets.view_dataset"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["resource_table"] = ResourceTable(self.object.resources.all())
        return ctx


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


class DatasetDeleteView(PermissionRequiredMixin, DeleteView):
    model = Dataset
    permission_required = "datasets.delete_dataset"

    def get_success_url(self):
        return reverse("datasets:dataset_list")


class ResourceDetailView(PermissionRequiredMixin, DetailView):
    model = Resource
    permission_required = "datasets.view_resource"

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        # Use inheritance manager to get the correct subclass instance
        return queryset.select_subclasses().get(pk=self.kwargs["pk"])

    def get_template_names(self):
        # Get the actual model class name (e.g., MapResource, RasterResource)
        model_name = self.object.__class__.__name__.lower()
        return [f"datasets/{model_name}_detail.html", "datasets/resource_detail.html"]


class ResourceCreateView(
    PermissionRequiredMixin,
    CreateView,
):
    permission_required = "datasets.add_resource"
    model = Resource
    form_class = ResourceForm

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dataset = None

    def get_dataset(self):
        if not self.dataset:
            self.dataset = Dataset.objects.get(pk=self.kwargs["dataset_pk"])
        return self.dataset

    def get_form_kwargs(self):
        args = super().get_form_kwargs()
        args["user"] = self.request.user
        args["dataset"] = self.get_dataset()
        return args

    def get_success_url(self):
        return reverse(
            "datasets:resource_update_metadata",
            kwargs={"dataset_pk": self.kwargs.get("dataset_pk"), "pk": self.object.pk},
        )


class ResourceUpdateView(
    PermissionRequiredMixin,
    # CreateBreadcrumbMixin,
    UpdateView,
):
    permission_required = "datasets.change_resource"
    model = Resource
    form_class = ResourceForm

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dataset = None

    def get_dataset(self):
        return self.object.dataset

    def get_form_kwargs(self):
        args = super().get_form_kwargs()
        args["user"] = self.request.user
        args["dataset"] = self.get_dataset()
        return args

    def get_success_url(self):
        return reverse(
            "datasets:resource_detail",
            kwargs={"dataset_pk": self.kwargs.get("dataset_pk"), "pk": self.object.pk},
        )


class DatasetRelationshipListView(
    PermissionRequiredMixin, SingleTableMixin, FilterView
):
    queryset = DatasetRelationship.objects.all()
    table_class = DatasetRelationshipTable
    permission_required = "datasets.list_datasetrelationship"
    filterset_class = DatasetRelationshipFilter

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                Q(source_id=self.kwargs["pk"]) | Q(destination_id=self.kwargs["pk"])
            )
        )


class DatasetRelationshipManageView(PermissionRequiredMixin, ListView):
    model = DatasetRelationship
    queryset = DatasetRelationship.objects.all()
    permission_required = "datasets.change_datasetrelationship"

    def get_template_names(self):
        if self.request.htmx:
            return "datasets/partials/form.html"
        return super().get_template_names()

    def get_queryset(self):
        return super().get_queryset().filter(source_id=self.kwargs["dataset_pk"])


class DatasetRelationshipCreateView(PermissionRequiredMixin, CreateView):
    form_class = DatasetRelationshipForm
    permission_required = "datasets.change_datasetrelationship"
    model = DatasetRelationship

    def get_template_names(self):
        if self.request.htmx:
            return "datasets/partials/form.html"
        return super().get_template_names()

    def get_queryset(self):
        return super().get_queryset().filter(source_id=self.kwargs["dataset_pk"])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        kwargs["user"] = self.request.user
        kwargs["source"] = Dataset.objects.get(pk=self.kwargs["dataset_pk"])

        return kwargs

    def get_success_url(self):
        return reverse(
            "datasets:dataset_relationship_update",
            kwargs={"dataset_pk": self.kwargs["dataset_pk"], "pk": self.object.pk},
        )


class DatasetRelationshipUpdateView(PermissionRequiredMixin, UpdateView):
    model = DatasetRelationship
    form_class = DatasetRelationshipForm
    permission_required = "datasets.change_datasetrelationship"
    slug_url_kwarg = "uuid"

    def get_template_names(self):
        if self.request.htmx:
            return "datasets/partials/form.html"
        return super().get_template_names()

    def get_queryset(self):
        return super().get_queryset().filter(source_id=self.kwargs["dataset_pk"])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        kwargs["user"] = self.request.user
        kwargs["source"] = Dataset.objects.get(pk=self.kwargs["dataset_pk"])
        kwargs["prefix"] = f"DR{self.object.id}"

        return kwargs

    def get_success_url(self):
        return reverse(
            "datasets:dataset_relationship_update",
            kwargs={"dataset_pk": self.kwargs["dataset_pk"], "pk": self.object.pk},
        )


class DatasetRelationshipDeleteView(PermissionRequiredMixin, DeleteView):
    model = DatasetRelationship
    permission_required = "datasets.delete_datasetrelationship"

    def get_queryset(self):
        return super().get_queryset().filter(source_id=self.kwargs["dataset_pk"])

    def get_template_names(self):
        if self.request.htmx:
            return "datasets/partials/form.html"
        return super().get_template_names()

    def form_valid(self, form):
        self.object.delete()
        return HttpResponse("")


# Mixins for Resource Views
class ResourceViewMixin:
    """Base mixin for resource views with common functionality."""

    def get_template_names(self):
        # Get the actual model class name (e.g., MapResource, RasterResource)
        model_name = self.object.__class__.__name__.lower()
        return [f"datasets/{model_name}_form.html", "datasets/resource_form.html"]

    def get_dataset(self):
        if hasattr(self.object, "dataset"):
            return self.object.dataset
        if not hasattr(self, "_dataset"):
            self._dataset = Dataset.objects.get(pk=self.kwargs["dataset_pk"])
        return self._dataset

    def get_form_kwargs(self):
        args = super().get_form_kwargs()
        args["user"] = self.request.user
        args["dataset"] = self.get_dataset()
        return args

    def get_success_url(self):
        return reverse(
            "datasets:resource_detail",
            kwargs={"dataset_pk": self.kwargs.get("dataset_pk"), "pk": self.object.pk},
        )


# Type-specific Resource Views
class MapResourceCreateView(PermissionRequiredMixin, ResourceViewMixin, CreateView):
    model = MapResource
    permission_required = "datasets.change_resource"
    form_class = MapResourceForm


class MapResourceUpdateView(PermissionRequiredMixin, ResourceViewMixin, UpdateView):
    model = MapResource
    permission_required = "datasets.change_resource"
    form_class = MapResourceForm


class RasterResourceCreateView(PermissionRequiredMixin, ResourceViewMixin, CreateView):
    model = RasterResource
    permission_required = "datasets.change_resource"
    form_class = RasterResourceForm


class RasterResourceUpdateView(PermissionRequiredMixin, ResourceViewMixin, UpdateView):
    model = RasterResource
    permission_required = "datasets.change_resource"
    form_class = RasterResourceForm


class TabularResourceCreateView(PermissionRequiredMixin, ResourceViewMixin, CreateView):
    model = TabularResource
    permission_required = "datasets.change_resource"
    form_class = TabularResourceForm


class TabularResourceUpdateView(PermissionRequiredMixin, ResourceViewMixin, UpdateView):
    model = TabularResource
    permission_required = "datasets.change_resource"
    form_class = TabularResourceForm


class PartitionedResourceCreateView(
    PermissionRequiredMixin, ResourceViewMixin, CreateView
):
    model = PartitionedResource
    permission_required = "datasets.change_resource"
    form_class = PartitionedResourceForm


class PartitionedResourceUpdateView(
    PermissionRequiredMixin, ResourceViewMixin, UpdateView
):
    model = PartitionedResource
    permission_required = "datasets.change_resource"
    form_class = PartitionedResourceForm


class ResourceDeleteView(PermissionRequiredMixin, DeleteView):
    model = Resource
    permission_required = "datasets.delete_resource"

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        return queryset.select_subclasses().get(pk=self.kwargs["pk"])

    def get_success_url(self):
        return reverse(
            "datasets:dataset_detail",
            kwargs={"pk": self.kwargs.get("dataset_pk")},
        )
