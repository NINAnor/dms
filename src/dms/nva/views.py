from django.contrib import messages
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import UpdateView
from rules.contrib.views import PermissionRequiredMixin

from dms.datasets.models import Dataset
from dms.projects.models import Project

from .forms import DatasetPublicationLinkForm, ProjectNVALinkForm


class ProjectNVALinkView(PermissionRequiredMixin, UpdateView):
    template_name = "nva/project_nva_link.html"
    form_class = ProjectNVALinkForm
    model = Project
    permission_required = "projects.change_project"
    pk_url_kwarg = "pk"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["project"] = self.object
        return kwargs

    def get_success_url(self):
        return reverse("projects:project_detail", kwargs={"pk": self.object.pk})


class DatasetPublicationLinkView(PermissionRequiredMixin, UpdateView):
    template_name = "nva/dataset_publication_link.html"
    form_class = DatasetPublicationLinkForm
    model = Dataset
    permission_required = "datasets.change_dataset"
    pk_url_kwarg = "pk"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["dataset"] = self.object
        return kwargs

    def form_valid(self, form):
        form.save()
        messages.success(
            self.request,
            _("Successfully linked NVA publications to %(dataset)s")
            % {"dataset": self.object},
        )
        return super().form_valid(form)
