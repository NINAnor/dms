import django_filters as filters
from dal import autocomplete

from dms.projects.models import Project

from .models import Service


class ServiceFilter(filters.FilterSet):
    projects = filters.ModelChoiceFilter(
        queryset=Project.objects.all(),
        widget=autocomplete.ModelSelect2(url="autocomplete:project"),
        method="filter_by_project",
        label="Project",
    )

    def filter_by_project(self, queryset, name, value):
        if value:
            return queryset.filter(projects=value)
        return queryset

    class Meta:
        model = Service
        fields = {"title": ["icontains"], "projects": ["exact"]}
