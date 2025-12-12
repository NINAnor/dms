import uuid

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from dal import autocomplete
from django import forms
from django.contrib.auth import get_user_model
from django.db import models
from django_jsonform.widgets import JSONFormWidget
from django_svelte_jsoneditor.widgets import SvelteJSONEditorWidget
from leaflet.forms.widgets import LeafletWidget

from dms.projects.models import Project

from .models import (
    ContributionType,
    Dataset,
    DatasetContribution,
    MapResource,
    PartitionedResource,
    RasterResource,
    Resource,
    TabularResource,
)

User = get_user_model()


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
        fields = ["title", "project", "embargo_end_date", "tags"]
        widgets = {
            "tags": autocomplete.TaggitSelect2(url="autocomplete:tag"),
            "project": autocomplete.ModelSelect2(url="autocomplete:my_project"),
            "embargo_end_date": forms.DateInput(
                format="%Y-%m-%d", attrs={"type": "date"}
            ),
        }


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
        fields = ["title", "version", "embargo_end_date", "tags"]
        widgets = {
            "embargo_end_date": forms.DateInput(
                format="%Y-%m-%d", attrs={"type": "date"}
            ),
            "tags": autocomplete.TaggitSelect2(url="autocomplete:tag"),
        }


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
        fields = ["metadata", "extent"]
        widgets = {"extent": LeafletWidget()}
        help_texts = {
            "extent": "Spatial extent can be computed automatically once you have "
            "registered accessible resources of the dataset"
        }


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
            "tags",
            "is_metadata_manual",
            "metadata",
            "extent",
        ]
        widgets = {
            "metadata": SvelteJSONEditorWidget,
            "extent": LeafletWidget(),
            "description": forms.Textarea(attrs={"rows": 10}),
            "tags": autocomplete.TaggitSelect2(url="autocomplete:tag"),
        }
        help_texts = {
            "extent": "Spatial extent can be computed automatically once you have "
            "registered accessible resources of the dataset",
            "is_metadata_manual": "If checked, the metadata will not be "
            "updated automatically",
            "metadata": "Automatically extracted for GDAL accessible and supported "
            "resources in case of manual metadata you can generate them using "
            "gdalinfo or ogr_info setting the output to json",
        }


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
            "tags",
            "is_metadata_manual",
            "metadata",
            "extent",
        ]
        widgets = ResourceForm.Meta.widgets


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
            "is_metadata_manual",
            "metadata",
        ]
        widgets = {
            "titiler": SvelteJSONEditorWidget,
        } | ResourceForm.Meta.widgets


class TabularResourceForm(ResourceForm):
    class Meta(ResourceForm.Meta):
        model = TabularResource
        fields = [
            "title",
            "uri",
            "description",
            "role",
            "access_type",
            "tags",
            "is_metadata_manual",
            "metadata",
        ]


class PartitionedResourceForm(ResourceForm):
    class Meta(ResourceForm.Meta):
        model = PartitionedResource


class DatasetContributorForm(forms.ModelForm):
    def __init__(self, *args, dataset, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_action = ""
        self.helper.add_input(Submit("submit", "Submit", **{"hr-post": "."}))
        self.dataset = dataset

        # Get all the users that are part of the project,
        # exclude those that already have a role
        qs = models.Q(
            pk__in=dataset.project.memberships.values_list("id", flat=True)
        ) & ~models.Q(
            pk__in=dataset.contributor_roles.values_list("user_id", flat=True)
        )

        # Include the selected user if the form is an update form
        if self.initial:
            qs = qs | models.Q(pk=self.initial["user"])

        self.fields["user"].queryset = User.objects.filter(qs)

    def clean_roles(self):
        return list(dict.fromkeys(self.cleaned_data["roles"]))

    def save(self, *args, **kwargs):
        instance = super().save(commit=False)
        instance.dataset = self.dataset
        instance.save()
        self.save_m2m()
        return instance

    class Meta:
        model = DatasetContribution
        fields = [
            "user",
            "roles",
        ]
        widgets = {
            "roles": JSONFormWidget(schema=ContributionType.SCHEMA),
        }


class ResourceConvertForm(forms.Form):
    TYPE_CLASSES = {
        "Resource": Resource,
        "MapResource": MapResource,
        "TabularResource": TabularResource,
        "RasterResource": RasterResource,
    }
    type = forms.ChoiceField(
        label="Convert to type",
        choices=(
            ("Resource", "Generic"),
            ("MapResource", "Map"),
            ("TabularResource", "Tabular"),
            ("RasterResource", "Raster"),
        ),
    )

    def __init__(self, *args, instance, user, dataset, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_action = ""
        self.helper.add_input(Submit("submit", "Submit"))
        self.resource = instance

        self.fields["type"].choices = list(
            filter(
                lambda v: v[0] != str(instance.__class__.__name__),
                self.fields["type"].choices,
            )
        )

    def save(self):
        self.resource.to_class(self.TYPE_CLASSES[self.cleaned_data.get("type")])
