import fiona
import rasterio as rio
import rules
from autoslug import AutoSlugField
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.urls import reverse
from django.utils.timezone import now
from django.utils.translation import gettext as _
from django_jsonform.models.fields import JSONField as JSONBField
from model_utils.managers import InheritanceManager
from rules.contrib.models import RulesModel

from .rules import (
    dataset_in_user_projects,
    resource_in_user_projects,
)
from .schemas import dataset_metadata


class Dataset(RulesModel):
    id = models.CharField(primary_key=True)
    version = models.IntegerField(null=True, blank=True)
    title = models.CharField()
    name = AutoSlugField(populate_from="title")
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.PROTECT,
        related_name="datasets",
        null=True,
    )
    created_at = models.DateTimeField(
        db_default=models.functions.Now(), verbose_name=_("Created at")
    )
    last_modified_at = models.DateTimeField(
        auto_now=True, verbose_name=_("Last modified at")
    )
    metadata = JSONBField(
        schema=dataset_metadata.schema, default=dict, encoder=DjangoJSONEncoder
    )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("datasets:dataset_detail", kwargs={"pk": self.pk})

    class Meta:
        rules_permissions = {
            "add": rules.is_authenticated,
            "view": rules.always_allow,
            "change": dataset_in_user_projects,
            "delete": rules.is_staff,
        }


class RelationshipType(models.TextChoices):
    CITES = "Cites", "Cites"
    REFERENCES = "References", "References"
    IS_PART_OF = "IsPartOf", "Is part of"
    IS_DERIVED_FROM = "IsDerivedFrom", "Is derived from"
    IS_TRANSLATION_OF = "IsTranslationOf", "Is translation of"
    IS_VERSION_OF = "IsVersionOf", "Is version of"


class DatasetRelationship(RulesModel):
    pk = models.CompositePrimaryKey("source_id", "target_id", "type")
    uuid = models.UUIDField(db_default=models.Func(function="gen_random_uuid"))
    source = models.ForeignKey(
        "Dataset", on_delete=models.CASCADE, related_name="source_rels"
    )
    target = models.ForeignKey(
        "Dataset", on_delete=models.CASCADE, related_name="target_rels"
    )
    type = models.CharField(choices=RelationshipType.choices)

    class Meta:
        rules_permissions = {
            "add": rules.is_authenticated,
            "view": rules.always_allow,
            "change": rules.is_authenticated,
            "delete": rules.is_authenticated,
        }


class Resource(RulesModel):
    class Role(models.TextChoices):
        DATA = "data", "Data"
        PRESENTATION = "presentation", "Presentation"
        DOCUMENTATION = "documentation", "Documentation"
        METADATA = "metadata", "Metadata"

    class ACCESSIBILITY(models.TextChoices):
        PUBLIC = "public", "Public"
        INTERNAL = "internal", "Internal"
        PERMISSIVE = "permissive", "Permission required"

    id = models.CharField(
        primary_key=True,
    )
    title = models.CharField(
        help_text="A name that describes the resource", default="", blank=True
    )
    description = models.CharField(default="", blank=True)
    name = models.CharField(null=True, blank=True)
    uri = models.CharField(
        verbose_name="URI of the resource",
        help_text="",
    )
    dataset = models.ForeignKey(
        "Dataset", on_delete=models.CASCADE, related_name="resources"
    )
    created_at = models.DateTimeField(
        db_default=models.functions.Now(), verbose_name=_("Created at")
    )
    last_modified_at = models.DateTimeField(
        auto_now=True, verbose_name=_("Last modified at")
    )
    metadata = models.JSONField(blank=True, null=True, encoder=DjangoJSONEncoder)
    role = models.CharField(blank=True, null=True)
    last_sync = models.JSONField(null=True, blank=True, encoder=DjangoJSONEncoder)

    objects = InheritanceManager()

    class Meta:
        rules_permissions = {
            "add": rules.is_authenticated,
            "view": rules.always_allow,
            "change": resource_in_user_projects,
            "delete": rules.is_staff,
        }

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse(
            "datasets:resource_detail",
            kwargs={"pk": self.pk, "dataset_pk": self.dataset_id},
        )

    @property
    def type(self):
        return None

    def infer_metadata(self):
        pass


class MapResource(Resource):
    @property
    def type(self):
        return "map"


class RasterResource(Resource):
    @property
    def type(self):
        return "raster"

    def infer_metadata(self):
        with rio.open(
            self.uri,
            driver=self.metadata.get("driver", default=None),
        ) as src:
            self.metadata = {"bounds": src.bounds, **src.profile}
            self.last_sync = {"timestamp": now()}
            self.save(update_fields=["metadata", "last_sync"])


class TabularResource(Resource):
    @property
    def type(self):
        return "tabular"

    def infer_metadata(self):
        with fiona.open(
            self.uri,
            ignore_geometry=True,
            layer=self.name,
            driver=self.metadata.get("driver", default=None),
        ) as src:
            self.metadata = {"bounds": src.bounds, **src.profile}
            self.last_sync = {"timestamp": now()}
            self.save(update_fields=["metadata", "last_sync"])


class PartitionedResource(Resource):
    @property
    def type(self):
        return "partitioned"
