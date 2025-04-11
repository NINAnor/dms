import uuid

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.urls import reverse_lazy

from dms.projects.models import Project

from .models import Dataset, DatasetRelationship, Resource, Storage


class DatasetForm(forms.ModelForm):
    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_action = ""
        # self.helper.include_media = False
        self.helper.add_input(Submit("submit", "Submit"))

        self.user = user
        self.fields["project"].required = True
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
        self.helper.add_input(Submit("submit", "Submit"))

        self.fields["storage"].required = True

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
            "type",
            "storage",
            "path",
        ]

        widgets = {
            "profile": forms.Select(
                attrs={
                    "hx-get": reverse_lazy("datasets:resource_type_list"),
                    "hx-trigger": "load,change",
                    "hx-target": "#id_type",
                    "hx-include": "#id_profile",
                }
            ),
            "type": forms.Select(choices=[]),
        }


class ResourceMetadataForm(BaseMetadataForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["schema"].widget.instance = self.instance

    class Meta:
        model = Resource
        fields = [
            "metadata",
            "schema",
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


class DatasetRelationshipForm(forms.ModelForm):
    def __init__(self, *args, user, source, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_action = ""
        # self.helper.include_media = False
        self.helper.add_input(Submit("submit", "Submit", **{"hr-post": "."}))
        self.source = source
        self.user = user

        self.fields["source"].disabled = True
        self.fields["source"].initial = source

    def save(self, *args, **kwargs):
        instance = super().save(commit=False)
        instance.source = self.source
        instance.save()
        self.save_m2m()
        return instance

    class Meta:
        model = DatasetRelationship
        fields = [
            "source",
            "type",
            "destination",
        ]
