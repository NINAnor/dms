import django_filters as filters
from dal import autocomplete
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db.models import Q
from leaflet.forms.widgets import LeafletWidget

from dms.projects.models import Project

from . import models


class DatasetFilter(filters.FilterSet):
    project = filters.ModelChoiceFilter(
        queryset=Project.objects.all(),
        widget=autocomplete.ModelSelect2(url="autocomplete:project"),
        method="filter_by_project",
        label="Project",
    )
    search = filters.CharFilter(
        label="Search", field_name="search", method="search_fulltext"
    )

    extent = filters.CharFilter(
        method="filter_extent",
        widget=LeafletWidget(
            attrs={
                "map_height": "400px",
                "map_width": "100%",
            }
        ),
    )

    def filter_extent(self, queryset, name, value):
        try:
            geom = self.form.cleaned_data.get("extent")
        except Exception:
            return queryset

        if not geom:
            return queryset

        return queryset.filter(extent__intersects=geom)

    def filter_by_project(self, queryset, name, value):
        if value:
            return queryset.filter(project=value)
        return queryset

    def search_fulltext(self, queryset, field_name, value):
        if not value:
            return queryset
        return (
            queryset.annotate(
                rank=SearchRank(
                    SearchVector("title", "name", "metadata"),
                    SearchQuery(value, search_type="websearch"),
                )
            )
            .filter(rank__gt=0.01)
            .order_by("-rank")
        )

    class Meta:
        model = models.Dataset
        fields = {"project": ["exact"], "version": ["exact"]}


class ResourceFilter(filters.FilterSet):
    dataset__project = filters.ModelChoiceFilter(
        queryset=Project.objects.all(),
        widget=autocomplete.ModelSelect2(url="autocomplete:project"),
        method="filter_by_project",
        label="Project",
    )
    dataset = filters.ModelChoiceFilter(
        queryset=models.Dataset.objects.all(),
        widget=autocomplete.ModelSelect2(url="autocomplete:dataset"),
        label="Dataset",
    )
    resource_type = filters.ChoiceFilter(
        method="filter_by_resource_type",
        label="Resource Type",
        choices=[
            ("resource", "Resource"),
            ("mapresource", "Map Resource"),
            ("tabularresource", "Tabular Resource"),
            ("rasterresource", "Raster Resource"),
            # ("partitioinedresource", "Partitioned Resource"),
        ],
    )

    extent = filters.CharFilter(
        method="filter_extent",
        widget=LeafletWidget(
            attrs={
                "map_height": "400px",
                "map_width": "100%",
            }
        ),
    )

    def filter_extent(self, queryset, name, value):
        try:
            geom = self.form.cleaned_data.get("extent")
        except Exception:
            return queryset

        if not geom:
            return queryset

        return queryset.filter(extent__intersects=geom)

    def filter_by_resource_type(self, queryset, name, value):
        if value:
            if value == "resource":
                filterset = {
                    "mapresource__isnull": True,
                    "tabularresource__isnull": True,
                    "rasterresource__isnull": True,
                    # "partitionedresource__isnull": True,
                }
            else:
                filterset = {value + "__isnull": False}
            return queryset.filter(**filterset)
        return queryset

    def filter_by_project(self, queryset, name, value):
        if value:
            return queryset.filter(dataset__project=value)
        return queryset

    class Meta:
        model = models.Resource
        fields = {
            "title": ["icontains"],
            "dataset__project": ["exact"],
            "dataset": ["exact"],
            "uri": ["startswith"],
        }


class ResourceRestFilter(ResourceFilter):
    is_cog = filters.BooleanFilter(method="filter_cog_resources")
    is_accessible = filters.BooleanFilter(method="filter_accessible_resources")
    search = filters.CharFilter(
        label="Search", field_name="search", method="search_fulltext"
    )

    def search_fulltext(self, queryset, field_name, value):
        if not value:
            return queryset
        return (
            queryset.annotate(
                rank=SearchRank(
                    SearchVector("title", "description"),
                    SearchQuery(value, search_type="websearch"),
                )
            )
            .filter(rank__gt=0.01)
            .order_by("-rank")
        )

    def filter_cog_resources(self, queryset, name, value):
        if value:
            return queryset.filter(
                metadata__driverShortName="GTiff",
                metadata__metadata__IMAGE_STRUCTURE__LAYOUT="COG",
            )
        return queryset

    def filter_accessible_resources(self, queryset, name, value):
        if value:
            return queryset.filter(last_sync__status="ok")
        return queryset

    class Meta(ResourceFilter.Meta):
        pass


class DatasetRelationshipFilter(filters.FilterSet):
    involves = filters.CharFilter(method="filter_by_dataset")

    def filter_by_dataset(self, queryset, name, value):
        if not value:
            return queryset

        return queryset.filter(Q(source_id=value) | Q(target_id=value)).distinct()

    class Meta:
        model = models.DatasetRelationship
        fields = (
            "source",
            "target",
            "type",
        )


class DataTableFilter(filters.FilterSet):
    is_pmtiles = filters.BooleanFilter(method="filter_pmtiles_layers")
    is_accessible = filters.BooleanFilter(method="filter_accessible_resources")
    search = filters.CharFilter(
        label="Search", field_name="search", method="search_fulltext"
    )

    def search_fulltext(self, queryset, field_name, value):
        if not value:
            return queryset
        return (
            queryset.annotate(
                rank=SearchRank(
                    SearchVector("resource__title", "resource__description", "name"),
                    SearchQuery(value, search_type="websearch"),
                )
            )
            .filter(rank__gt=0.01)
            .order_by("-rank")
        )

    def filter_pmtiles_layers(self, queryset, name, value):
        if value:
            return queryset.filter(
                resource__metadata__driverShortName="PMTiles",
            )
        return queryset

    def filter_accessible_resources(self, queryset, name, value):
        if value:
            return queryset.filter(resource__last_sync__status="ok")
        return queryset

    class Meta:
        model = models.DataTable
        fields = (
            "resource",
            "name",
        )
