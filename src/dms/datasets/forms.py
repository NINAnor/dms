import uuid

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

from dms.projects.models import Project

from .models import Dataset, Resource, Storage


class DatasetForm(forms.ModelForm):
    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_action = ""
        # self.helper.include_media = False
        self.helper.add_input(Submit("submit", "Submit"))

        self.user = user
        self.fields["project"].queryset = Project.objects.filter(
            members__user=self.user
        )

    def save(self, *args, **kwargs):
        instance = super().save(commit=False)
        if not instance.id:
            instance.id = uuid.uuid4()
        instance.save()
        self.save_m2m()
        return instance

    class Meta:
        model = Dataset
        fields = ["title", "project", "profile"]


class DatasetUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_action = ""
        self.helper.add_input(Submit("submit", "Submit"))

    def save(self, *args, **kwargs):
        instance = super().save(commit=False)
        if not instance.id:
            instance.id = uuid.uuid4()
        instance.save()
        self.save_m2m()
        return instance

    class Meta:
        model = Dataset
        fields = [
            "title",
        ]


class BaseMetadataForm(forms.ModelForm):
    metadata_field_name = "metadata"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_action = ""
        self.helper.add_input(Submit("submit", "Submit"))
        self.fields[self.metadata_field_name].widget.instance = self.instance


class DatasetMetadataForm(BaseMetadataForm):
    class Meta:
        model = Dataset
        fields = [
            "metadata",
        ]


class ResourceForm(forms.ModelForm):
    def __init__(self, *args, user, dataset, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_action = ""
        # self.helper.include_media = False
        self.helper.add_input(Submit("submit", "Submit"))

        self.user = user
        self.dataset = dataset

    def save(self, *args, **kwargs):
        instance = super().save(commit=False)
        if not instance.id:
            instance.id = uuid.uuid5(self.dataset.id, instance.name)
        if not instance.dataset_id:
            instance.dataset = self.dataset
        instance.save()
        self.save_m2m()
        return instance

    class Meta:
        model = Resource
        fields = [
            "title",
            "profile",
            "storage",
            "path",
        ]


class StorageForm(forms.ModelForm):
    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_action = ""
        # self.helper.include_media = False
        self.helper.add_input(Submit("submit", "Submit"))

        self.user = user
        self.fields["project"].queryset = Project.objects.filter(
            members__user=self.user
        )
        self.fields["project"].required = not user.is_staff

    def save(self, *args, **kwargs):
        instance = super().save(commit=False)
        if not instance.id:
            instance.id = uuid.uuid4()
        instance.save()
        self.save_m2m()
        return instance

    class Meta:
        model = Storage
        fields = ["title", "project", "type"]


class StorageConfigForm(BaseMetadataForm):
    metadata_field_name = "config"

    class Meta:
        model = Storage
        fields = [
            "config",
        ]
