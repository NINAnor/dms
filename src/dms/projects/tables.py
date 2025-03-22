import django_tables2 as tables

from .models import DMP, Project


class ProjectTable(tables.Table):
    number = tables.LinkColumn()
    end_date = tables.DateColumn(format="d/m/Y")
    start_date = tables.DateColumn(format="d/m/Y")

    class Meta:
        model = Project
        fields = (
            "number",
            "name",
            "status",
            "start_date",
            "end_date",
            "section",
            "category",
            "customer",
            "tags",
        )
        template_name = "django_tables2/bootstrap.html"

    def render_tags(self, value, record):
        return ", ".join(value.all().values_list("name", flat=True))


class DMPTable(tables.Table):
    name = tables.LinkColumn()
    created_at = tables.DateColumn(format="d/m/Y")
    modified_at = tables.DateColumn(format="d/m/Y")

    class Meta:
        model = DMP
        fields = (
            "name",
            "created_at",
            "modified_at",
            "project",
        )
        template_name = "django_tables2/bootstrap.html"
