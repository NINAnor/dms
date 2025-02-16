from django_filters import FilterSet

from . import models


class ProjectFilter(FilterSet):
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
        }
