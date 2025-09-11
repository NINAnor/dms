from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from dal import autocomplete
from django import forms

from .models import DMP, Project, ProjectMembership


class ProjectForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_action = ""
        self.helper.include_media = False
        self.helper.add_input(Submit("submit", "Submit"))

        self.fields["tags"].required = False

    class Meta:
        model = Project
        fields = [
            "description",
            "topics",
            "tags",
        ]

        widgets = {
            "tags": autocomplete.TaggitSelect2(url="autocomplete:tag"),
            "topics": autocomplete.ModelSelect2Multiple(
                url="autocomplete:project_topic"
            ),
        }


class DMPForm(forms.ModelForm):
    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_action = ""
        self.helper.include_media = False
        self.helper.add_input(Submit("submit", "Submit"))

        self.user = user
        self.fields["project"].queryset = Project.objects.filter(
            number__in=user.memberships.filter(
                role=ProjectMembership.Role.OWNER
            ).values_list("project")
        )

    def save(self, *args, **kwargs):
        instance = super().save(commit=False)
        instance.owner = self.user
        instance.save()
        self.save_m2m()
        return instance

    class Meta:
        model = DMP
        fields = ["name", "project", "external_reference", "external_file"]
