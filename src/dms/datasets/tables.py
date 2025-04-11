import django_tables2 as tables

from .models import Dataset, DatasetRelationship, Resource, Storage


class DatasetTable(tables.Table):
    title = tables.LinkColumn()
    created_at = tables.DateColumn(format="d/m/Y")
    last_modified_at = tables.DateColumn(format="d/m/Y")

    class Meta:
        model = Dataset
        fields = (
            "title",
            "name",
            "created_at",
            "last_modified_at",
            "project",
        )
        template_name = "django_tables2/bootstrap.html"


class ResourceTable(tables.Table):
    title = tables.LinkColumn()
    created_at = tables.DateColumn(format="d/m/Y")
    last_modified_at = tables.DateColumn(format="d/m/Y")

    class Meta:
        model = Resource
        fields = (
            "title",
            "created_at",
            "last_modified_at",
            "profile",
            "storage",
            "path",
        )
        template_name = "django_tables2/bootstrap.html"


class StorageTable(tables.Table):
    title = tables.LinkColumn()
    created_at = tables.DateColumn(format="d/m/Y")
    last_modified_at = tables.DateColumn(format="d/m/Y")

    class Meta:
        model = Storage
        fields = (
            "title",
            "type",
            "created_at",
            "last_modified_at",
            "project",
        )
        template_name = "django_tables2/bootstrap.html"


class DatasetRelationshipTable(tables.Table):
    class Meta:
        model = DatasetRelationship
        fields = ("id", "source", "destination", "type")
        template_name = "django_tables2/bootstrap.html"
