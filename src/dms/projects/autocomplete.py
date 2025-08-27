from dal import autocomplete

from .models import Category, Project, ProjectTopic, Section


class ProjectAutocomplete(autocomplete.Select2QuerySetView):
    model = Project
    search_fields = [
        "name",
        "number",
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


class ProjectTopicAutocomplete(autocomplete.Select2QuerySetView):
    model = ProjectTopic
    search_fields = [
        "id",
    ]


class MyProjectAutocomplete(autocomplete.Select2QuerySetView):
    model = Project
    search_fields = [
        "name",
        "number",
    ]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_authenticated:
            qs = qs.filter(members__user=self.request.user)
        return qs
