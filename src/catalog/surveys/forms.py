from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

from .models import Survey


class SurveyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_action = ""
        self.helper.include_media = False
        self.helper.add_input(Submit("submit", "Submit"))

    class Meta:
        model = Survey
        fields = [
            "name",
        ]
