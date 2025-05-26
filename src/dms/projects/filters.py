import django_filters as filters
from dal import autocomplete
from django import forms
from django.contrib.auth import get_user_model
from taggit.models import Tag

from . import models

User = get_user_model()


class DMPFilter(filters.FilterSet):
    project = filters.ModelChoiceFilter(
        queryset=models.Project.objects.all(),
        widget=autocomplete.ModelSelect2(url="autocomplete:project"),
        method="filter_by_project",
        label="Project",
    )

    def filter_by_project(self, queryset, name, value):
        if value:
            return queryset.filter(project=value)
        return queryset

    class Meta:
        model = models.DMP
        fields = {"name": ["icontains"], "project": ["exact"]}


class ProjectFilter(filters.FilterSet):
    leader = filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        to_field_name="username",
        widget=autocomplete.ModelSelect2(url="autocomplete:user"),
        method="filter_by_leader",
        label="Leader",
    )
    participant = filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        widget=autocomplete.ModelSelect2(url="autocomplete:user"),
        method="filter_by_participant",
        label="Participant",
        to_field_name="username",
    )
    topics = filters.ModelMultipleChoiceFilter(
        queryset=models.ProjectTopic.objects.all(),
        widget=autocomplete.ModelSelect2Multiple(url="autocomplete:project_topic"),
    )
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        widget=autocomplete.ModelSelect2Multiple(url="autocomplete:tag"),
        method="filter_tags",
    )

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        super().__init__(data, queryset, request=request, prefix=prefix)
        self.filters["category"].extra["widget"] = autocomplete.ModelSelect2(
            url="autocomplete:category"
        )
        self.filters["section"].extra["widget"] = autocomplete.ModelSelect2(
            url="autocomplete:section"
        )

        self.filters["start_date__gte"].extra["widget"] = forms.DateInput(
            format="%Y-%m-%d", attrs={"type": "date"}
        )
        self.filters["end_date__lte"].extra["widget"] = forms.DateInput(
            format="%Y-%m-%d", attrs={"type": "date"}
        )

    def filter_by_participant(self, queryset, name, value):
        if value:
            return queryset.filter(memberships=value)
        return queryset

    def filter_by_leader(self, queryset, name, value):
        if value:
            return queryset.filter(
                members__user=value, members__role=models.ProjectMembership.Role.OWNER
            )
        return queryset

    def filter_tags(self, queryset, name, value):
        if value:
            return queryset.filter(tags__name__in=value).distinct()
        return queryset

    class Meta:
        model = models.Project
        fields = {
            "number": ["istartswith"],
            "name": ["icontains"],
            "status": ["exact"],
            "category": ["exact"],
            "section": ["exact"],
            "start_date": ["gte"],
            "end_date": ["lte"],
            "customer": ["istartswith"],
            "topics": ["exact"],
        }
