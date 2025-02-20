from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from dal import autocomplete
from django import forms

from .models import Project


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
            "topics": autocomplete.ModelSelect2Multiple(url="autocomplete:topic"),
            "tags": autocomplete.TaggitSelect2(url="autocomplete:tag"),
        }
