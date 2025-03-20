from django.contrib import admin
from solo.admin import SingletonModelAdmin

from .models import (
    Category,
    Project,
    ProjectMembership,
    ProjectsConfiguration,
    Section,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    pass


class ProjectMembershipInline(admin.TabularInline):
    model = ProjectMembership


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    search_fields = ["number", "name"]
    list_filter = []
    list_display = [
        "number",
        "name",
    ]

    inlines = [ProjectMembershipInline]


@admin.register(ProjectMembership)
class ProjectMembershipAdmin(admin.ModelAdmin):
    search_fields = ["project__number", "project__name", "user__email"]
    list_filter = ["role"]
    list_display = ["project", "user", "role"]


admin.site.register(ProjectsConfiguration, SingletonModelAdmin)
