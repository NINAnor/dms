import rules
from django.db import models
from rules.contrib.models import RulesModel


class Service(RulesModel):
    id = models.CharField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField(null=True)
    keywords = models.JSONField(null=True, blank=True)
    technologies = models.JSONField(null=True, blank=True)

    related = models.ManyToManyField("self", blank=True, through="ServiceRelated")
    projects = models.ManyToManyField(
        "projects.Project", blank=True, through="ProjectService"
    )

    class Meta:
        rules_permissions = {
            "add": rules.is_staff,
            "view": rules.always_allow,
            "change": rules.is_staff,
            "delete": rules.is_staff,
        }


class ProjectService(RulesModel):
    pk = models.CompositePrimaryKey("project", "service")
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.DO_NOTHING,
        db_constraint=False,
    )
    service = models.ForeignKey(
        "Service",
        on_delete=models.DO_NOTHING,
        db_constraint=False,
    )

    class Meta:
        rules_permissions = {
            "add": rules.is_staff,
            "view": rules.always_allow,
            "change": rules.is_staff,
            "delete": rules.is_staff,
        }


class ServiceRelated(RulesModel):
    pk = models.CompositePrimaryKey("from_service", "to_service")
    from_service = models.ForeignKey(
        "Service",
        on_delete=models.DO_NOTHING,
        db_constraint=False,
        related_name="related_to_service",
    )
    to_service = models.ForeignKey(
        "Service",
        on_delete=models.DO_NOTHING,
        db_constraint=False,
        related_name="related_from_service",
    )

    class Meta:
        rules_permissions = {
            "add": rules.is_staff,
            "view": rules.always_allow,
            "change": rules.is_staff,
            "delete": rules.is_staff,
        }


class Contributor(RulesModel):
    class Role(models.TextChoices):
        MAINTAINER = "maintainer", "Maintainer"
        OWNER = "owner", "Owner"

    service = models.ForeignKey(
        Service,
        related_name="contributors",
        on_delete=models.CASCADE,
        db_constraint=False,
    )
    email = models.EmailField()
    role = models.CharField(choices=Role.choices)
    pk = models.CompositePrimaryKey("service", "email", "role")

    class Meta:
        rules_permissions = {
            "add": rules.is_staff,
            "view": rules.always_allow,
            "change": rules.is_staff,
            "delete": rules.is_staff,
        }


class Resource(RulesModel):
    class AccessType(models.TextChoices):
        public = "public", "Public available"
        private = "private", "Available only to NINA users"
        permit = "permit", "Request access"

    id = models.CharField(primary_key=True)
    title = models.CharField(null=True)
    description = models.TextField(null=True)
    uri = models.CharField()
    service = models.ForeignKey(
        Service,
        related_name="resources",
        on_delete=models.DO_NOTHING,
        db_constraint=False,
    )
    access = models.CharField(choices=AccessType.choices)
    internal_ref = models.CharField(null=True)
    external = models.BooleanField(default=False)

    class Meta:
        rules_permissions = {
            "add": rules.is_staff,
            "view": rules.always_allow,
            "change": rules.is_staff,
            "delete": rules.is_staff,
        }
