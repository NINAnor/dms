from django.urls import path

from catalog.projects.autocomplete import (
    CategoryAutocomplete,
    ProjectAutocomplete,
    SectionAutocomplete,
    TopicAutocomplete,
)
from catalog.users.autocomplete import UserAutocomplete

app_name = "autocomplete"
urlpatterns = [
    path("category/", CategoryAutocomplete.as_view(), name="category"),
    path("section/", SectionAutocomplete.as_view(), name="section"),
    path("project/", ProjectAutocomplete.as_view(), name="project"),
    path("topic/", TopicAutocomplete.as_view(), name="topic"),
    path("user/", UserAutocomplete.as_view(), name="user"),
]
