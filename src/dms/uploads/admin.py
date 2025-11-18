from django.contrib import admin
from django.db.models.fields.json import JSONField
from django_svelte_jsoneditor.widgets import SvelteJSONEditorWidget

from .models import HookRequest


@admin.register(HookRequest)
class HookRequestAdmin(admin.ModelAdmin):
    formfield_overrides = {
        JSONField: {"widget": SvelteJSONEditorWidget},
    }
