from django.contrib import admin
from django.forms import ModelForm
from django_svelte_jsoneditor.widgets import SvelteJSONEditorWidget
from import_export.admin import ImportExportModelAdmin
from jsonfield import JSONField

from .models import Dataset, Schema
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


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    form = DatasetForm
