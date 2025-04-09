import rules
from django.contrib.postgres.fields import ArrayField
from django.db import models
from rules.contrib.models import RulesModel


class Service(RulesModel):
    id = models.CharField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField(null=True)
    keywords = ArrayField(
        models.CharField(),
        default=list,
        blank=True,
    )
    technologies = ArrayField(
        models.CharField(),
        default=list,
        blank=True,
    )

    related = models.ManyToManyField(
        "self",
        symmetrical=False,
        blank=True,
    )
    projects = models.ManyToManyField(
        "projects.Project",
        blank=True,
        through="ProjectService",
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


class Contributor(RulesModel):
    class Role(models.TextChoices):
        MAINTAINER = "maintainer", "Maintainer"
        OWNER = "owner", "Owner"

    service = models.ForeignKey(
        Service, related_name="contributors", on_delete=models.CASCADE
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
