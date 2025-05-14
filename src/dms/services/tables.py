import django_tables2 as tables
from django.urls import reverse
from django.utils.html import format_html

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
            "projects",
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


class ServiceResourceTable(tables.Table):
    service = tables.LinkColumn()

    class Meta:
        model = Resource
        fields = (
            "service",
            "title",
            "uri",
            "type",
            "description",
            "access",
            "external",
            "internal_ref",
            "service__projects",
        )
        template_name = "django_tables2/bootstrap.html"

    def render_uri(self, value):
        if value.startswith("http"):
            return format_html(f'<a href="{value}">{value}</a>')
        return value

    def render_service__projects(self, value):
        text = [
            f'<a href="{reverse("projects:project_detail", kwargs={"pk": p.pk})}">{p.pk}</a>'  # noqa: E501
            for p in value.all()
            if p
        ]
        return format_html(", ".join(text))


class ContributorTable(tables.Table):
    class Meta:
        model = Contributor
        fields = (
            "email",
            "role",
        )
        template_name = "django_tables2/bootstrap.html"
