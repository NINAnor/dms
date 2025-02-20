from dal import autocomplete
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import path
from taggit.models import Tag

from catalog.projects.autocomplete import (
    CategoryAutocomplete,
    ProjectAutocomplete,
    SectionAutocomplete,
    TopicAutocomplete,
)
from catalog.users.autocomplete import UserAutocomplete


class TagAutocomplete(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    model = Tag
    search_fields = "name"

    def get_create_option(self, context, q):
        return []


app_name = "autocomplete"
urlpatterns = [
    path("category/", CategoryAutocomplete.as_view(), name="category"),
    path("section/", SectionAutocomplete.as_view(), name="section"),
    path("project/", ProjectAutocomplete.as_view(), name="project"),
    path(
        "topic/",
        TopicAutocomplete.as_view(),
        name="topic",
    ),
    path("user/", UserAutocomplete.as_view(), name="user"),
    path("tag/", TagAutocomplete.as_view(), name="tag"),
]
