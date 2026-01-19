import logging
import traceback

from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import (
    DMP,
    Category,
    DMPSchema,
    Project,
    ProjectMembership,
    ProjectTopic,
    Section,
)


class ProjectResource(resources.ModelResource):
    def save_instance(self, instance, is_create, row, **kwargs):
        super().save_instance(instance, is_create, row, **kwargs)

        try:
            if row["topics"] and not is_create:
                for t in row["topics"].split(","):
                    topic, _ = ProjectTopic.objects.get_or_create(id=t)
                    instance.topics.add(topic)
        except Exception:
            logging.error(traceback.format_exc())

    class Meta:
        model = Project
        fields = (
            "number",
            "description",
            "topics",
        )
        import_id_fields = ["number"]


@admin.register(ProjectTopic)
class ProjectTopicAdmin(admin.ModelAdmin):
    pass


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    pass


@admin.register(DMP)
class DMPAdmin(admin.ModelAdmin):
    pass


@admin.register(DMPSchema)
class DMPSchemaAdmin(admin.ModelAdmin):
    pass


class ProjectMembershipInline(admin.TabularInline):
    model = ProjectMembership


@admin.register(Project)
class ProjectAdmin(ImportExportModelAdmin):
    search_fields = ["number", "name"]
    list_filter = []
    list_display = [
        "number",
        "name",
    ]

    inlines = [ProjectMembershipInline]
    resource_classes = [ProjectResource]


@admin.register(ProjectMembership)
class ProjectMembershipAdmin(admin.ModelAdmin):
    search_fields = ["project__number", "project__name", "user__email"]
    list_filter = ["role"]
    list_display = ["project", "user", "role"]
