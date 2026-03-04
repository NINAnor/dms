from django.contrib import admin

from .models import Resource, Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("id", "title")
    search_fields = ("id", "title")


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "service",
        "featured",
        "featured_order",
        "featured_icon",
    )
    list_filter = ("featured", "service")
    list_editable = ("featured", "featured_order", "featured_icon")
    search_fields = ("id", "title")
    ordering = ("featured_order",)
