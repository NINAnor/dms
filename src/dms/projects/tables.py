import django_tables2 as tables

from .models import DMP, Project


class ProjectTable(tables.Table):
    number = tables.LinkColumn()
    end_date = tables.DateColumn(format="d/m/Y")
    start_date = tables.DateColumn(format="d/m/Y")

    def render_status(self, value, record):
        return record.get_status_display()

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
            "topics",
            "customer",
            "tags",
        )
        template_name = "django_tables2/bootstrap.html"

    def render_tags(self, value, record):
        return ", ".join(value.all().values_list("name", flat=True))

    def render_topics(self, value, record):
        return ", ".join(value.all().values_list("id", flat=True))


class DMPTable(tables.Table):
    name = tables.LinkColumn()
    created_at = tables.DateColumn(format="d/m/Y")
    modified_at = tables.DateColumn(format="d/m/Y")
    featured_at = tables.BooleanColumn(verbose_name="Featured")

    class Meta:
        model = DMP
        fields = (
            "name",
            "created_at",
            "updated_at",
            "project",
        )
        template_name = "django_tables2/bootstrap.html"
