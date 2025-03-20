import django_tables2 as tables

from .models import Project


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
            "topics",
        )
        template_name = "django_tables2/bootstrap.html"
