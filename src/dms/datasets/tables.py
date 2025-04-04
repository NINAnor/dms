import django_tables2 as tables

from .models import Dataset


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
