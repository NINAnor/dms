import uuid

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from dal import autocomplete
from django import forms
from django_svelte_jsoneditor.widgets import SvelteJSONEditorWidget

from dms.projects.models import Project

from .models import (
    Dataset,
    DatasetRelationship,
    MapResource,
    PartitionedResource,
    RasterResource,
    Resource,
    TabularResource,
)


class DatasetForm(forms.ModelForm):
    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_action = ""
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
        fields = ["title", "project"]
        widgets = {"project": autocomplete.ModelSelect2(url="autocomplete:my_project")}


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

        self.user = user
        self.dataset = dataset

    def save(self, *args, **kwargs):
        instance = super().save(commit=False)
        if not instance.id:
            instance.id = uuid.uuid4()
        if not instance.dataset_id:
            instance.dataset = self.dataset
        instance.save()
        self.save_m2m()
        return instance

    class Meta:
        model = Resource
        fields = [
            "title",
            "uri",
            "description",
            "role",
            "access_type",
            "metadata",
        ]
        widgets = {"metadata": SvelteJSONEditorWidget}


class MapResourceForm(ResourceForm):
    class Meta(ResourceForm.Meta):
        model = MapResource
        fields = [
            "title",
            "uri",
            "description",
            "role",
            "access_type",
            "map_type",
            "metadata",
        ]


class RasterResourceForm(ResourceForm):
    class Meta(ResourceForm.Meta):
        model = RasterResource
        fields = [
            "title",
            "uri",
            "description",
            "role",
            "access_type",
            "titiler",
            "metadata",
        ]
        widgets = {
            "metadata": SvelteJSONEditorWidget,
            "titiler": SvelteJSONEditorWidget,
        }


class TabularResourceForm(ResourceForm):
    class Meta(ResourceForm.Meta):
        model = TabularResource
        fields = [
            "title",
            "uri",
            "name",
            "description",
            "role",
            "access_type",
            "metadata",
        ]


class PartitionedResourceForm(ResourceForm):
    class Meta(ResourceForm.Meta):
        model = PartitionedResource


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
            "target",
        ]
        widgets = {"target": autocomplete.ModelSelect2(url="autocomplete:dataset")}
