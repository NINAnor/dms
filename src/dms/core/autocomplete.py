from dal import autocomplete
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import path
from taggit.models import Tag

from dms.datasets.autocomplete import DatasetAutocomplete
from dms.projects.autocomplete import (
    CategoryAutocomplete,
    ProjectAutocomplete,
    ProjectTopicAutocomplete,
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
    path("projects/category/", CategoryAutocomplete.as_view(), name="category"),
    path("projects/section/", SectionAutocomplete.as_view(), name="section"),
    path("projects/project/", ProjectAutocomplete.as_view(), name="project"),
    path("projects/topic/", ProjectTopicAutocomplete.as_view(), name="project_topic"),
    path("user/", UserAutocomplete.as_view(), name="user"),
    path("tag/", TagAutocomplete.as_view(), name="tag"),
    path("datasets/dataset/", DatasetAutocomplete.as_view(), name="dataset"),
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
