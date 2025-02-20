from dal import autocomplete

from .models import (
    Category,
    Project,
    Section,
    Topic,
)


class ProjectAutocomplete(autocomplete.Select2QuerySetView):
    model = Project
    search_fields = [
        "name",
        "number",
    ]


class TopicAutocomplete(ProjectAutocomplete):
    model = Topic


class SectionAutocomplete(ProjectAutocomplete):
    model = Section


class CategoryAutocomplete(ProjectAutocomplete):
    model = Category
