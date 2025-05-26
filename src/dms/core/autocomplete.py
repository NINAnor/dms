from dal import autocomplete
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import path
from taggit.models import Tag

from dms.datasets.autocomplete import DatasetAutocomplete
from dms.projects.autocomplete import (
    CategoryAutocomplete,
    ProjectAutocomplete,
    SectionAutocomplete,
)
from dms.services.autocomplete import (
    ServiceKeywordAutocomplete,
    ServiceTechnologyAutocomplete,
)
from dms.users.autocomplete import UserAutocomplete


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
    path("user/", UserAutocomplete.as_view(), name="user"),
    path("tag/", TagAutocomplete.as_view(), name="tag"),
    path("dataset/", DatasetAutocomplete.as_view(), name="dataset"),
    path(
        "services/keyword/",
        ServiceKeywordAutocomplete.as_view(),
        name="service_keyword",
    ),
    path(
        "services/technology/",
        ServiceTechnologyAutocomplete.as_view(),
        name="service_technology",
    ),
]
