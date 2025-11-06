from crispy_forms.helper import FormHelper
from django import forms
from django.utils.translation import gettext_lazy as _

from dms.datasets.models import Dataset
from dms.projects.models import Project

from .models import (
    NVAProject,
    NVAProjectRelationship,
    NVAPublication,
    NVAPublicationDataset,
)


class ProjectNVALinkForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = []  # We don't update any fields directly on the Project model

    nva_projects = forms.ModelMultipleChoiceField(
        queryset=NVAProject.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label=_("NVA Projects"),
        help_text=_("Select one or more NVA projects to link to this project"),
    )

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop("project")
        super().__init__(*args, **kwargs)

        # Set initial values based on existing relationships
        self.fields["nva_projects"].initial = NVAProject.objects.filter(
            projects=self.project
        )

        # Set up crispy forms helper
        self.helper = FormHelper(self)
        self.helper.form_method = "post"
        self.helper.add_input(
            forms.Submit("submit", _("Save"), css_class="btn-primary")
        )

    def save(self):
        from django.db import transaction

        with transaction.atomic():
            # Clear existing relationships
            NVAProjectRelationship.objects.filter(project=self.project).delete()

            # Create new relationships
            for nva_project in self.cleaned_data["nva_projects"]:
                NVAProjectRelationship.objects.create(
                    project=self.project,
                    nva_project=nva_project,
                )


class DatasetPublicationLinkForm(forms.ModelForm):
    class Meta:
        model = Dataset
        fields = []  # We don't update any fields directly on the Dataset model

    nva_publications = forms.ModelMultipleChoiceField(
        queryset=NVAPublication.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label=_("NVA Publications"),
        help_text=_("Select one or more NVA publications to link to this dataset"),
    )

    def __init__(self, *args, **kwargs):
        self.dataset = kwargs.pop("dataset")
        super().__init__(*args, **kwargs)

        # Set initial values based on existing relationships
        self.fields["nva_publications"].initial = NVAPublication.objects.filter(
            nvapublicationdataset__dataset=self.dataset
        )

        # Set up crispy forms helper
        self.helper = FormHelper(self)
        self.helper.form_method = "post"
        self.helper.add_input(
            forms.Submit("submit", _("Save"), css_class="btn-primary")
        )

    def save(self):
        from django.db import transaction

        with transaction.atomic():
            # Clear existing relationships
            NVAPublicationDataset.objects.filter(dataset=self.dataset).delete()

            # Create new relationships
            for publication in self.cleaned_data["nva_publications"]:
                NVAPublicationDataset.objects.create(
                    dataset=self.dataset,
                    nva_publication=publication,
                )
