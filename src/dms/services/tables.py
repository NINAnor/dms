import django_tables2 as tables

from .models import Contributor, Resource, Service


class ServiceTable(tables.Table):
    title = tables.LinkColumn()

    def render_keywords(self, value):
        return ", ".join(value)

    def render_technologies(self, value):
        return ", ".join(value)

    class Meta:
        model = Service
        fields = (
            "title",
            "description",
            "keywords",
            "technologies",
        )
        template_name = "django_tables2/bootstrap.html"


class ResourceTable(tables.Table):
    class Meta:
        model = Resource
        fields = (
            "title",
            "uri",
            "type",
            "description",
            "access",
            "external",
            "internal_ref",
        )
        template_name = "django_tables2/bootstrap.html"


class ContributorTable(tables.Table):
    class Meta:
        model = Contributor
        fields = (
            "email",
            "role",
        )
        template_name = "django_tables2/bootstrap.html"
