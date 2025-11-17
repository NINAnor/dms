# from django.db.models import Prefetch
# from django.urls import reverse_lazy
import json

from django.contrib import messages
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
from django_svelte_jsoneditor.widgets import SvelteJSONEditorWidget
from django_tables2.views import SingleTableMixin
from rules.contrib.views import PermissionRequiredMixin
from view_breadcrumbs import (
    CreateBreadcrumbMixin,
    DetailBreadcrumbMixin,
    ListBreadcrumbMixin,
    UpdateBreadcrumbMixin,
)

from dms.frontend.views import FrontendMixin
from dms.shared.views import ActionView

from .conf import settings
from .filters import DatasetFilter, ResourceFilter
from .forms import (
    DatasetContributorForm,
    DatasetForm,
    DatasetMetadataForm,
    DatasetUpdateForm,
    MapResourceForm,
    PartitionedResourceForm,
    RasterResourceForm,
    ResourceForm,
    TabularResourceForm,
)
from .models import (
    Dataset,
    DatasetContribution,
    DatasetRelationship,
    MapResource,
    PartitionedResource,
    RasterResource,
    RelationshipType,
    Resource,
    TabularResource,
)
from .tables import (
    DatasetContributionTable,
    DatasetRelationshipTable,
    DatasetTable,
    DataTableListTable,
    ResourceListTable,
    ResourceTable,
)


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
    table_class = ResourceListTable
    filterset_class = ResourceFilter
    permission_required = "datasets.view_resource"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_subclasses()
            .select_related("dataset", "dataset__project")
        )


class DatasetDetailView(PermissionRequiredMixin, DetailBreadcrumbMixin, DetailView):
    model = Dataset
    permission_required = "datasets.view_dataset"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["contributor_table"] = DatasetContributionTable(
            self.object.contributor_roles.all()
        )
        ctx["resource_table"] = ResourceTable(
            self.object.resources.select_subclasses().all()
        )

        widget = SvelteJSONEditorWidget(
            props={"mode": "view", "readOnly": True, "navigationBar": False},
            attrs={"id": "metadata_preview"},
            wrapper_class="svelte-jsoneditor-wrapper",
        )
        ctx["metadata_preview"] = widget.render(
            name="metadata_preview", value=json.dumps(self.object.metadata, indent=2)
        )

        ctx["FEATURE_URL"] = self.request.build_absolute_uri(
            reverse("api_v1:datasets-geojson-feature", kwargs={"pk": self.object.pk})
        )

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


class DatasetCloneView(PermissionRequiredMixin, ActionView):
    model = Dataset
    permission_required = "datasets.edit_dataset"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("project")
            .prefetch_related("contributor_roles", "tags")
        )

    def execute(self):
        self.cloned_dataset = self.object.clone()
        messages.success(
            self.request, f'Dataset "{self.object.title}" was successfully cloned.'
        )

    def get_success_url(self):
        return reverse("datasets:dataset_detail", kwargs={"pk": self.cloned_dataset.pk})


class DatasetComputeExtentView(PermissionRequiredMixin, ActionView):
    model = Dataset
    permission_required = "datasets.edit_dataset"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("project")
            .prefetch_related("contributor_roles", "resources", "tags")
        )

    def execute(self):
        self.object.compute_extent()
        messages.success(
            self.request, f'Dataset "{self.object.title}" spatial extent was computed'
        )

    def get_success_url(self):
        return reverse("datasets:dataset_detail", kwargs={"pk": self.object.pk})


class ResourceDetailView(PermissionRequiredMixin, DetailView):
    model = Resource
    permission_required = "datasets.view_resource"

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        # Use inheritance manager to get the correct subclass instance
        return (
            queryset.select_subclasses()
            .prefetch_related("data_tables")
            .get(pk=self.kwargs["pk"])
        )

    def _get_model_name(self):
        return self.object.__class__.__name__.lower()

    def get_context_tabularresource(self):
        snippets = []

        BASE_TEMPLATE_PATH = "datasets/snippets/"

        try:
            is_spatial = len(self.object.metadata["layers"][0]["geometryFields"]) > 0
        except Exception:
            is_spatial = False

        if (
            self.object.metadata
            and self.object.metadata.get("driverShortName") == "Parquet"
        ):
            snippets.append(
                {
                    "template": BASE_TEMPLATE_PATH + "r-duckdb-parquet",
                    "lang": "r",
                    "title": "R (DuckDB)",
                    "spatial": is_spatial,
                }
            )
            snippets.append(
                {
                    "template": BASE_TEMPLATE_PATH + "python-duckdb-parquet",
                    "lang": "python",
                    "title": "Python (DuckDB)",
                    "spatial": is_spatial,
                }
            )
            if is_spatial:
                snippets.append(
                    {
                        "template": BASE_TEMPLATE_PATH + "python-geopandas",
                        "lang": "python",
                        "title": "Python (GeoPandas)",
                        "spatial": is_spatial,
                    }
                )
                snippets.append(
                    {
                        "template": BASE_TEMPLATE_PATH + "r-sf",
                        "lang": "r",
                        "title": "R (Simple Feature Objects)",
                        "spatial": is_spatial,
                    }
                )

            snippets.append(
                {
                    "template": BASE_TEMPLATE_PATH + "duckdb-sql",
                    "lang": "sql",
                    "title": "DuckDB (SQL)",
                    "spatial": is_spatial,
                }
            )

        return {
            "snippets": snippets,
            "snippets_default": snippets[0].get("template") if snippets else "",
            "data_table": DataTableListTable(
                self.object.data_tables.all(), prefix="data_"
            ),
        }

    def get_context_mapresource(self):
        return {"NINA_MAP_PREVIEW": settings.DATASETS_NINA_MAP_PREVIEW}

    def get_context_rasterresource(self):
        snippets = []

        BASE_TEMPLATE_PATH = "datasets/snippets/"

        if self.object.metadata and self.object.metadata.get("driverShortName"):
            snippets.append(
                {
                    "template": BASE_TEMPLATE_PATH + "r-terra",
                    "lang": "r",
                    "title": "R (Terra)",
                }
            )
            snippets.append(
                {
                    "template": BASE_TEMPLATE_PATH + "python-rasterio",
                    "lang": "python",
                    "title": "Python (Rasterio)",
                }
            )

        return {
            "snippets": snippets,
            "snippets_default": snippets[0].get("template") if snippets else "",
        }

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        widget = SvelteJSONEditorWidget(
            props={"mode": "view", "readOnly": True, "navigationBar": False},
            attrs={"id": "metadata_preview"},
            wrapper_class="svelte-jsoneditor-wrapper",
        )
        ctx["metadata_preview"] = widget.render(
            name="metadata_preview", value=json.dumps(self.object.metadata, indent=2)
        )

        ctx["FEATURE_URL"] = self.request.build_absolute_uri(
            reverse("api_v1:resources-geojson-feature", kwargs={"pk": self.object.pk})
        )

        return (
            ctx | getattr(self, f"get_context_{self._get_model_name()}", lambda: {})()
        )

    def get_template_names(self):
        # Get the actual model class name (e.g., MapResource, RasterResource)
        model_name = self._get_model_name()
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
            "datasets:resource_detail",
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


class DatasetRelationshipListView(PermissionRequiredMixin, FrontendMixin, ListView):
    queryset = DatasetRelationship.objects.all()
    table_class = DatasetRelationshipTable
    permission_required = "datasets.view_datasetrelationship"
    frontend_module = "relationships"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                Q(source_id=self.kwargs["pk"])
                | Q(target_id=self.kwargs["pk"])
                | Q(source__target_rels__source_id=self.kwargs["pk"])
                | Q(source__target_rels__target_id=self.kwargs["pk"])
                | Q(source__source_rels__target_id=self.kwargs["pk"])
                | Q(source__source_rels__source_id=self.kwargs["pk"])
                #
                | Q(target__target_rels__source_id=self.kwargs["pk"])
                | Q(target__target_rels__target_id=self.kwargs["pk"])
                | Q(target__source_rels__source_id=self.kwargs["pk"])
                | Q(target__source_rels__target_id=self.kwargs["pk"])
            )
            .distinct()
        )

    def get_initial_data(self):
        initial = super().get_initial_data()
        qs = self.get_queryset()

        datasets = Dataset.objects.filter(
            Q(id=self.kwargs["pk"])
            | Q(target_rels__source_id=self.kwargs["pk"])
            | Q(source_rels__target_id=self.kwargs["pk"])
        ).prefetch_related("source_rels")

        initial["nodes"] = [
            {
                "id": ds.id,
                "data": {
                    "label": ds.title,
                    "relationshipTypes": list(
                        set(ds.source_rels.values_list("type", flat=True))
                    ),
                    "url": reverse("datasets:dataset_detail", kwargs={"pk": ds.id}),
                },
                "position": {
                    "y": 0,
                    "x": 0,
                },
                "type": "dataset",
            }
            for ds in datasets
        ]

        initial["edges"] = [
            {
                "id": rel.uuid,
                "source": rel.source_id,
                "target": rel.target_id,
                "sourceHandle": rel.type,
                "type": "smart",
            }
            for rel in qs.all()
        ]

        initial["relTypes"] = [
            {"label": label, "value": value}
            for value, label in RelationshipType.choices
        ]

        initial["urls"] = {
            "datasetList": reverse("api_v1:datasets-list"),
            "datasetRelationshipList": reverse("api_v1:dataset-relationships-list"),
        }

        return initial


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

    def form_valid(self, form):
        response = super().form_valid(form)
        # Add message for new resource creation (only on CreateView)
        if hasattr(self, "object") and self.object._state.adding:
            messages.info(
                self.request,
                "Metadata collection has been queued and"
                " will be processed asynchronously.",
            )
        return response

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


class ResourceRefreshMetadataView(PermissionRequiredMixin, ActionView):
    model = Resource
    permission_required = "datasets.change_resource"

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        return queryset.select_subclasses().get(pk=self.kwargs["pk"])

    def execute(self):
        self.object.infer_metadata()
        messages.info(
            self.request,
            "Metadata collection has been queued and will be processed asynchronously.",
        )

    def get_success_url(self):
        return reverse(
            "datasets:resource_detail",
            kwargs={"dataset_pk": self.kwargs.get("dataset_pk"), "pk": self.object.pk},
        )


class DatasetContributionManageView(PermissionRequiredMixin, ListView):
    model = DatasetContribution
    queryset = DatasetContribution.objects.all()
    permission_required = "datasets.change_datasetcontribution"

    def get_template_names(self):
        if self.request.htmx:
            return "datasets/partials/form.html"
        return super().get_template_names()

    def get_queryset(self):
        return super().get_queryset().filter(dataset_id=self.kwargs["dataset_pk"])


class DatasetContributionCreateView(PermissionRequiredMixin, CreateView):
    form_class = DatasetContributorForm
    permission_required = "datasets.change_datasetcontribution"
    model = DatasetContribution

    def get_template_names(self):
        if self.request.htmx:
            return "datasets/partials/datasetcontribution_form.html"
        return super().get_template_names()

    def get_queryset(self):
        return super().get_queryset().filter(dataset_id=self.kwargs["dataset_pk"])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["dataset"] = Dataset.objects.get(pk=self.kwargs["dataset_pk"])
        return kwargs

    def get_success_url(self):
        return reverse(
            "datasets:dataset_contribution_update",
            kwargs={
                "dataset_pk": self.kwargs["dataset_pk"],
                "user_pk": self.object.user_id,
            },
        )


class DatasetContributionUpdateView(PermissionRequiredMixin, UpdateView):
    model = DatasetContribution
    form_class = DatasetContributorForm
    permission_required = "datasets.change_datasetcontribution"
    slug_url_kwarg = "user_pk"
    slug_field = "user_id"

    def get_template_names(self):
        if self.request.htmx:
            return "datasets/partials/datasetcontribution_form.html"
        return super().get_template_names()

    def get_queryset(self):
        return super().get_queryset().filter(dataset_id=self.kwargs["dataset_pk"])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["dataset"] = Dataset.objects.get(pk=self.kwargs["dataset_pk"])
        kwargs["prefix"] = f"DC{self.object.user_id}"
        return kwargs

    def get_success_url(self):
        return reverse(
            "datasets:dataset_contribution_update",
            kwargs={
                "dataset_pk": self.kwargs["dataset_pk"],
                "user_pk": self.object.user_id,
            },
        )


class DatasetContributionDeleteView(PermissionRequiredMixin, DeleteView):
    model = DatasetContribution
    permission_required = "datasets.delete_datasetcontribution"
    slug_url_kwarg = "user_pk"
    slug_field = "user_id"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                dataset_id=self.kwargs["dataset_pk"], user_id=self.kwargs["user_pk"]
            )
        )

    def get_template_names(self):
        if self.request.htmx:
            return "datasets/partials/datasetcontribution_form.html"
        return super().get_template_names()

    def form_valid(self, form):
        self.object.delete()
        return HttpResponse("")


class UploadResourceView(PermissionRequiredMixin, FrontendMixin, DetailView):
    queryset = Dataset.objects.all()
    permission_required = "datasets.change_dataset"
    frontend_module = "upload"

    def get_initial_data(self):
        initial = super().get_initial_data()

        initial["endpoint"] = reverse(
            "api_v1:datasets-upload-resource", kwargs={"pk": self.get_object().pk}
        )

        return initial
