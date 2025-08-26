from django.contrib import admin
from django.forms import ModelForm

from .models import (
    Dataset,
    Resource,
)


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    pass


class ResourceForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # manually set the current instance on the widget
        self.fields["metadata"].widget.instance = self.instance
        self.fields["schema"].widget.instance = self.instance


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    form = ResourceForm
