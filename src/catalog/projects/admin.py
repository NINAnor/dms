from django.contrib import admin

from .models import (
    Project,
    ProjectMembership,
)


class ProjectMembershipInline(admin.TabularInline):
    model = ProjectMembership


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    search_fields = ["number", "name"]
    list_filter = ["active"]
    list_display = ["number", "name", "active"]

    inlines = [ProjectMembershipInline]


@admin.register(ProjectMembership)
class ProjectMembershipAdmin(admin.ModelAdmin):
    search_fields = ["project__number", "project__name", "user__email"]
    list_filter = ["role"]
    list_display = ["project", "user", "role"]
