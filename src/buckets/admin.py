from django.contrib import admin

from .models import Storage


@admin.register(Storage)
class StorageAdmin(admin.ModelAdmin):
    list_display = ("name", "bucket_name", "endpoint_url", "is_global", "canned_acl")
    list_filter = ("is_global", "canned_acl")
    search_fields = ("name", "bucket_name", "endpoint_url")
