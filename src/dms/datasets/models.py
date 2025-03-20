from uuid import uuid4

from autoslug import AutoSlugField
from django.contrib.gis.db import models as geo_models
from django.db import models
from django.utils.translation import gettext as _


class Dataset(geo_models.Model):
    class Visibility(models.TextChoices):
        PUBLIC = "public", "Public"
        INTERNAL = "internal", "Internal"
        PROTECTED = "protected", "Protected"
        DRAFT = "draft", "Draft"

    title = models.CharField()
    slug = AutoSlugField(populate_from="title")
    uid = models.UUIDField(default=uuid4)
    project = models.ForeignKey("projects.Project", on_delete=models.PROTECT)
    validated_at = models.DateTimeField(
        null=True, blank=True, verbose_name=_("Validated at")
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    last_modified_at = models.DateTimeField(
        auto_now=True, verbose_name=_("Last modified at")
    )
    notes = models.TextField()


class Resource(models.Model):
    class Type(models.TextChoices):
        TABULAR = "tabular", "Tabular"
        VECTOR = "vector", "Vector"
        RASTER = "raster", "Raster"
        LINK = "link", "Link"

    name = models.CharField()
    position = models.CharField()
    type = models.CharField(choices=Type.choices)
    config = models.JSONField(default=dict)
    dataset = models.ForeignKey("Dataset", on_delete=models.CASCADE)
    schema = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    last_modified_at = models.DateTimeField(
        auto_now=True, verbose_name=_("Last modified at")
    )
