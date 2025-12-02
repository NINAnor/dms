from django.contrib import admin
from django.db.models.fields.json import JSONField
from django_svelte_jsoneditor.widgets import SvelteJSONEditorWidget

from .models import HookRequest


@admin.register(HookRequest)
class HookRequestAdmin(admin.ModelAdmin):
    formfield_overrides = {
        JSONField: {"widget": SvelteJSONEditorWidget},
    }
    list_display = ("id", "type", "created_at", "completed_at", "user")
    readonly_fields = ("id", "event", "created_at", "completed_at")
    search_fields = ("id", "type", "user__username", "user__email")
    list_filter = ("type", "created_at", "completed_at", "user")
