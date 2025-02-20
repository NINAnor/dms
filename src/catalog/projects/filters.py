import django_filters as filters
from dal import autocomplete
from django.contrib.auth import get_user_model

from . import models

User = get_user_model()


class ProjectFilter(filters.FilterSet):
    participant = filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        widget=autocomplete.ModelSelect2(url="autocomplete:user"),
        method="filter_by_participant",
        label="Participant",
        to_field_name="username",
    )
    leader = filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        to_field_name="username",
        widget=autocomplete.ModelSelect2(url="autocomplete:user"),
        method="filter_by_leader",
        label="Leader",
    )

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        super().__init__(data, queryset, request=request, prefix=prefix)
        self.filters["category"].extra["widget"] = autocomplete.ModelSelect2(
            url="autocomplete:category"
        )
        self.filters["section"].extra["widget"] = autocomplete.ModelSelect2(
            url="autocomplete:section"
        )
        self.filters["topics"].extra["widget"] = autocomplete.ModelSelect2Multiple(
            url="autocomplete:topic"
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
            "topics": ["exact"],
        }
