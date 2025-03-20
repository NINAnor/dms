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


class TopicAutocomplete(autocomplete.Select2QuerySetView):
    model = Topic
    create_field = "text"
    validate_create = True
    search_fields = [
        "text",
    ]


class SectionAutocomplete(autocomplete.Select2QuerySetView):
    model = Section
    search_fields = [
        "text",
    ]


class CategoryAutocomplete(autocomplete.Select2QuerySetView):
    model = Category
    search_fields = [
        "text",
    ]
