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

    def render_tags(self, value, record):
        return ", ".join([str(v) for v in value.all()])

    class Meta:
        model = Dataset
        fields = (
            "title",
            "name",
            "version",
            "created_at",
            "last_modified_at",
            "project",
            "tags",
        )
        template_name = "django_tables2/bootstrap.html"
        order_by = "-last_modified_at"


class ResourceTable(tables.Table):
    title = tables.LinkColumn()
    created_at = tables.DateColumn(format="d/m/Y")
    last_modified_at = tables.DateColumn(format="d/m/Y")
    resource_type = tables.Column(empty_values=(), verbose_name="Type")

    def render_resource_type(self, record):
        return record.__class__.__name__

    def render_uri(self, value, record):
        if record.dataset.under_embargo:
            return None
        if value and (value.startswith("http://") or value.startswith("https://")):
            return mark_safe(f'<a href="{value}" target="_blank">{value}</a>')  # noqa: S308
        return value

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
        order_by = "-last_modified_at"


class ResourceListTable(ResourceTable):
    dataset = tables.LinkColumn()
    project = tables.Column(empty_values=(), orderable=False)

    def render_uri(self, value, record):
        if record.dataset.under_embargo:
            return None
        if value and (value.startswith("http://") or value.startswith("https://")):
            return mark_safe(f'<a href="{value}" target="_blank">{value}</a>')  # noqa: S308
        return value

    def render_project(self, record):
        project = record.dataset.project
        return mark_safe(f'<a href="{project.get_absolute_url()}">{project}</a>')  # noqa: S308

    class Meta(ResourceTable.Meta):
        fields = (
            "title",
            "resource_type",
            "created_at",
            "last_modified_at",
            "uri",
            "dataset",
        )
        template_name = "django_tables2/bootstrap.html"


class DatasetRelationshipTable(tables.Table):
    class Meta:
        model = DatasetRelationship
        fields = ("id", "source", "target", "type")
        template_name = "django_tables2/bootstrap.html"


CONTRIBUTION_TYPE = dict(ContributionType.choices)


class DatasetContributionTable(tables.Table):
    external = tables.BooleanColumn()

    class Meta:
        model = DatasetContribution
        template_name = "django_tables2/bootstrap.html"
        fields = (
            "user",
            "email",
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


class DatasetRelated(tables.Table):
    relationType = tables.Column()
    relatedIdentifier = tables.Column()
    resourceTypeGeneral = tables.Column()
    relatedIdentifierType = tables.Column()

    class Meta:
        template_name = "django_tables2/bootstrap.html"


class DatasetInternalRelated(tables.Table):
    source = tables.LinkColumn()
    type = tables.Column()
    target = tables.LinkColumn()

    class Meta:
        template_name = "django_tables2/bootstrap.html"


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
