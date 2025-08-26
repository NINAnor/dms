import django_filters as filters
from dal import autocomplete

from dms.projects.models import Project

from . import models


class DatasetFilter(filters.FilterSet):
    project = filters.ModelChoiceFilter(
        queryset=Project.objects.all(),
        widget=autocomplete.ModelSelect2(url="autocomplete:project"),
        method="filter_by_project",
        label="Project",
    )

    def filter_by_project(self, queryset, name, value):
        if value:
            return queryset.filter(project=value)
        return queryset

    class Meta:
        model = models.Dataset
        fields = {"title": ["icontains"], "project": ["exact"], "version": ["exact"]}


class ResourceFilter(filters.FilterSet):
    dataset__project = filters.ModelChoiceFilter(
        queryset=Project.objects.all(),
        widget=autocomplete.ModelSelect2(url="autocomplete:project"),
        method="filter_by_project",
        label="Project",
    )

    def filter_by_dataset__project(self, queryset, name, value):
        if value:
            return queryset.filter(dataset__project=value)
        return queryset

    class Meta:
        model = models.Resource
        fields = {
            "title": ["icontains"],
            "name": ["exact"],
            "dataset__project": ["exact"],
            "dataset": ["exact"],
        }


class DatasetRelationshipFilter(filters.FilterSet):
    class Meta:
        model = models.DatasetRelationship
        fields = (
            "source",
            "target",
            "type",
        )
