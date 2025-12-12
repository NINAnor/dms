import django_tables2 as tables
from django.utils.safestring import mark_safe

from .models import (
    ContributionType,
    Dataset,
    DatasetContribution,
    DatasetRelationship,
    DataTable,
    Resource,
)


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


CONTRIBUTION_TYPE = dict(ContributionType.choices)


class DatasetContributionTable(tables.Table):
    # user = tables.LinkColumn()

    class Meta:
        model = DatasetContribution
        template_name = "django_tables2/bootstrap.html"
        fields = (
            "user",
            "roles",
        )

    def render_roles(self, record):
        return ", ".join(map(lambda r: CONTRIBUTION_TYPE[r], record.roles))


def safe_nested_get(obj, path):
    el = obj
    for p in path.split("."):
        el = el.get(p)
        if not el:
            break

    return el


class DataTableListTable(tables.Table):
    def render_fields(self, record):
        return mark_safe(  # noqa: S308
            "".join(
                list(
                    map(
                        lambda x: f"<li>{x.get('name')} ({x.get('type')})</li>",
                        record.fields,
                    )
                )
            )
        )

    def render_geometryFields(self, record):
        return mark_safe(  # noqa: S308
            "".join(
                [
                    (
                        f"<li>{x.get('name')} ({x.get('type')} "
                        f"{safe_nested_get(x, 'coordinateSystem.projjson.name')}</li>"
                    )
                    for x in (record.geometryFields or [])
                ]
            )
        )

    class Meta:
        model = DataTable
        fields = (
            "name",
            "count",
            "is_spatial",
            "fields",
            "geometryFields",
        )
        template_name = "django_tables2/bootstrap.html"
