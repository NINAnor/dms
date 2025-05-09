from django.contrib import admin
from django.forms import ModelForm
from django_svelte_jsoneditor.widgets import SvelteJSONEditorWidget
from import_export.admin import ImportExportModelAdmin
from jsonfield import JSONField

from .models import (
    Dataset,
    DatasetRelationship,
    Resource,
    Schema,
    Storage,
)
from .resources import SchemaResource


@admin.register(Schema)
class SchemaAdmin(ImportExportModelAdmin):
    resource_classes = [SchemaResource]
    formfield_overrides = {
        JSONField: {
            "widget": SvelteJSONEditorWidget,
        }
    }


class DatasetForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # manually set the current instance on the widget
        self.fields["metadata"].widget.instance = self.instance
        self.fields["fetch"].widget = SvelteJSONEditorWidget()


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    form = DatasetForm


class StorageForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # manually set the current instance on the widget
        self.fields["config"].widget.instance = self.instance


@admin.register(Storage)
class StorageAdmin(admin.ModelAdmin):
    form = StorageForm


class ResourceForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # manually set the current instance on the widget
        self.fields["metadata"].widget.instance = self.instance
        self.fields["schema"].widget.instance = self.instance


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    form = ResourceForm


@admin.register(DatasetRelationship)
class DatasetRelationshipAdmin(admin.ModelAdmin):
    pass
