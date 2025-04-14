# from django.db.models import Prefetch
# from django.urls import reverse_lazy

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponse
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
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

from . import schemas
from .filters import DatasetFilter, DatasetRelationshipFilter, StorageFilter
from .forms import (
    DatasetForm,
    DatasetMetadataForm,
    DatasetRelationshipForm,
    DatasetUpdateForm,
    ResourceForm,
    ResourceMetadataForm,
    StorageConfigForm,
    StorageForm,
)
from .models import Dataset, DatasetRelationship, Resource, Storage
from .tables import DatasetRelationshipTable, DatasetTable, ResourceTable, StorageTable


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


class ResourceDetailView(PermissionRequiredMixin, DetailView):
    model = Resource
    permission_required = "datasets.view_resource"


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
            "datasets:resource_update_metadata",
            kwargs={"dataset_pk": self.kwargs.get("dataset_pk"), "pk": self.object.pk},
        )


class ResourceMetadataUpdateView(
    PermissionRequiredMixin,
    UpdateView,
):
    permission_required = "datasets.change_resource"
    model = Resource
    form_class = ResourceMetadataForm


class StorageListView(
    LoginRequiredMixin, ListBreadcrumbMixin, SingleTableMixin, FilterView
):
    model = Storage
    table_class = StorageTable
    filterset_class = StorageFilter

    def get_queryset(self):
        return super().get_queryset()


class StorageDetailView(PermissionRequiredMixin, DetailView):
    model = Storage
    permission_required = "datasets.view_storage"


class StorageCreateView(
    PermissionRequiredMixin,
    CreateView,
):
    permission_required = "datasets.add_storage"
    model = Storage
    form_class = StorageForm

    def get_form_kwargs(self):
        args = super().get_form_kwargs()
        args["user"] = self.request.user
        return args


class StorageUpdateView(
    PermissionRequiredMixin,
    UpdateView,
):
    permission_required = "datasets.change_storage"
    model = Storage
    form_class = StorageForm

    def get_form_kwargs(self):
        args = super().get_form_kwargs()
        args["user"] = self.request.user
        return args


class StorageConfigView(
    PermissionRequiredMixin,
    UpdateView,
):
    permission_required = "datasets.change_storage"
    model = Storage
    form_class = StorageConfigForm

    def get_form_kwargs(self):
        args = super().get_form_kwargs()
        return args


class ResourceMediaTypeOptionsView(TemplateView):
    template_name = "datasets/options.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx["options"] = []

        profile = self.request.GET.get("profile")
        if profile:
            allowed = schemas.resource_types.RESOURCE_TYPE_MAP.get(profile, {})
            ctx["options"] = list((k.value, k.label) for k in allowed.keys())

        return ctx


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
