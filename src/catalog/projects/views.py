from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin

from .filters import ProjectFilter
from .models import Project
from .tables import ProjectTable


class ProjectListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    model = Project
    table_class = ProjectTable
    filterset_class = ProjectFilter

    def get_queryset(self):
        return super().get_queryset()


class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
