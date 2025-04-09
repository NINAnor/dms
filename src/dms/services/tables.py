import django_tables2 as tables

from .models import Service


class ServiceTable(tables.Table):
    def render_keywords(self, value):
        return ", ".join(value)

    class Meta:
        model = Service
        fields = (
            "title",
            "keywords",
        )
        template_name = "django_tables2/bootstrap.html"
