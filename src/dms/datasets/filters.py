import django_filters as filters
from dal import autocomplete
from django.contrib.postgres.search import SearchQuery, SearchVector
from django.db.models import Q

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

    def filter_by_project(self, queryset, name, value):
        if value:
            return queryset.filter(project=value)
        return queryset

    def search_fulltext(self, queryset, field_name, value):
        if not value:
            return queryset
        return queryset.annotate(
            search=SearchVector("title", "name", "metadata")
        ).filter(search=SearchQuery(value))

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
        }


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
