import django_tables2 as tables

from .models import Dataset, DatasetRelationship, Resource


class DatasetTable(tables.Table):
    title = tables.LinkColumn()
    created_at = tables.DateColumn(format="d/m/Y")
    last_modified_at = tables.DateColumn(format="d/m/Y")

    class Meta:
        model = Dataset
        fields = (
            "title",
            "name",
            "version",
            "created_at",
            "last_modified_at",
            "project",
        )
        template_name = "django_tables2/bootstrap.html"


class ResourceTable(tables.Table):
    title = tables.LinkColumn()
    created_at = tables.DateColumn(format="d/m/Y")
    last_modified_at = tables.DateColumn(format="d/m/Y")
    resource_type = tables.Column(empty_values=(), verbose_name="Type")

    def render_resource_type(self, record):
        return record.__class__.__name__

    class Meta:
        model = Resource
        fields = (
            "title",
            "resource_type",
            "created_at",
            "last_modified_at",
            "uri",
        )
        template_name = "django_tables2/bootstrap.html"


class ResourceListTable(ResourceTable):
    dataset = tables.LinkColumn()
    project = tables.LinkColumn()

    class Meta(ResourceTable.Meta):
        fields = (
            "title",
            "resource_type",
            "created_at",
            "last_modified_at",
            "uri",
            "dataset",
            "project",
        )
        template_name = "django_tables2/bootstrap.html"


class DatasetRelationshipTable(tables.Table):
    class Meta:
        model = DatasetRelationship
        fields = ("id", "source", "target", "type")
        template_name = "django_tables2/bootstrap.html"
