from urllib.parse import urlencode

import fiona
import rasterio as rio
import requests
import rules
from autoslug import AutoSlugField
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.urls import reverse
from django.utils.timezone import now
from django.utils.translation import gettext as _
from django_jsonform.models.fields import JSONField as JSONBField
from django_lifecycle import AFTER_SAVE, LifecycleModelMixin, hook
from django_lifecycle.conditions import WhenFieldHasChanged
from model_utils.managers import InheritanceManager
from procrastinate.contrib.django import app
from rasterio.errors import RasterioError
from rules.contrib.models import RulesModel

from .conf import settings
from .rules import (
    dataset_in_user_projects,
    resource_in_user_projects,
)
from .schemas import dataset_metadata


class Dataset(RulesModel):
    id = models.CharField(primary_key=True)
    version = models.CharField(null=True, blank=True)
    title = models.CharField()
    name = AutoSlugField(populate_from="title")
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.PROTECT,
        related_name="datasets",
        null=True,
        db_constraint=False,
    )
    created_at = models.DateTimeField(
        db_default=models.functions.Now(),
        verbose_name=_("Created at"),
        blank=True,
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


class Resource(LifecycleModelMixin, RulesModel):
    class Role(models.TextChoices):
        DATA = "data", "Data"
        PRESENTATION = "presentation", "Presentation"
        DOCUMENTATION = "documentation", "Documentation"
        METADATA = "metadata", "Metadata"

    class AccessType(models.TextChoices):
        PUBLIC = "public", "Public"
        INTERNAL = "internal", "Internal"
        PERMISSION_REQUIRED = "permission_required", "Permission required"

    id = models.CharField(
        primary_key=True,
    )
    title = models.CharField(
        help_text="A name that describes the resource", default="", blank=True
    )
    description = models.CharField(default="", blank=True)
    uri = models.CharField(
        verbose_name="URI of the resource",
        help_text="",
    )
    dataset = models.ForeignKey(
        "Dataset", on_delete=models.CASCADE, related_name="resources"
    )
    created_at = models.DateTimeField(
        db_default=models.functions.Now(), verbose_name=_("Created at"), blank=True
    )
    last_modified_at = models.DateTimeField(
        auto_now=True, verbose_name=_("Last modified at")
    )
    metadata = models.JSONField(blank=True, null=True, encoder=DjangoJSONEncoder)
    role = models.CharField(blank=True, null=True, choices=Role.choices)
    access_type = models.CharField(
        blank=True, null=True, default=AccessType.INTERNAL, choices=AccessType.choices
    )

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
    def detail_url(self):
        self.__class__.objects.get_subclass(id=self.pk).get_absolute_url()

    @property
    def type(self):
        return None

    def _get_http_headers(self):
        """Extract Last-Modified and ETag headers for HTTP resources."""
        if not self.uri.startswith("http"):
            return {}

        try:
            response = requests.head(self.uri, timeout=30)
            headers = {}

            if "Last-Modified" in response.headers:
                headers["last_modified"] = response.headers["Last-Modified"]

            return headers
        except requests.RequestException:
            return {}

    def infer_metadata(self, deferred=True):
        if deferred:
            app.configure_task(name="dms.datasets.tasks.infer_metadata_task").defer(
                resource_id=self.pk
            )
            return

        http_headers = self._get_http_headers()
        if http_headers:
            if not self.metadata:
                self.metadata = {}
            self.metadata["http_headers"] = http_headers
            self.last_sync = {"timestamp": now(), "status": "ok"}
            self.save(update_fields=["metadata", "last_sync"])

    @hook(
        AFTER_SAVE,
        condition=WhenFieldHasChanged("uri", has_changed=True),
        on_commit=True,
    )
    def populate(self):
        self.__class__.objects.get_subclass(id=self.pk).infer_metadata()

    def get_edit_url(self):
        return reverse(
            "datasets:resource_update",
            kwargs={"dataset_pk": self.dataset_id, "pk": self.pk},
        )

    @property
    def edit_url(self):
        return self.__class__.objects.get_subclass(id=self.pk).get_edit_url()


class MapResource(Resource):
    class Type(models.TextChoices):
        NINA = "nina", "Nina Map configuration"
        URL = "url", "Link to a published map"

    map_type = models.CharField(default=Type.URL, choices=Type.choices)

    def get_edit_url(self):
        return reverse(
            "datasets:mapresource_update",
            kwargs={"dataset_pk": self.dataset_id, "pk": self.pk},
        )

    @property
    def type(self):
        return "map"


class RasterResource(Resource):
    @property
    def type(self):
        return "raster"

    titiler = models.JSONField(default=dict, verbose_name="Titiler configuration")

    @property
    def preview_url(self):
        params = {
            "colormap_name": "viridis",
            **self.titiler,
            "url": self.uri,
        }
        params = [(k, v) for k, v in params.items()] + [
            ("rescale", f"{s['min']},{s['max']}") for s in self.metadata["statistics"]
        ]
        return settings.DATASETS_TITILER_URL + "/cog/preview/?" + urlencode(params)

    def infer_metadata(self, deferred=True):
        if deferred:
            app.configure_task(name="dms.datasets.tasks.infer_metadata_task").defer(
                resource_id=self.pk
            )
            return

        try:
            with rio.open(
                self.uri,
                driver=self.metadata.get("driver", None) if self.metadata else None,
            ) as src:
                stats = src.stats(approx=True)
                metadata = {
                    "bounds": src.bounds,
                    "driver": src.driver,
                    "crs": src.crs.to_string(),
                    "dtypes": src.dtypes,
                    "nodata": src.nodata,
                    "width": src.width,
                    "height": src.height,
                    "count": src.count,
                    "tiled": src.is_tiled,
                    "compression": str(src.compression),
                    "descriptions": src.descriptions,
                    "indexes": src.indexes,
                    "interleaving": str(src.interleaving),
                    "tags": src.tags(),
                    "photometric": src.photometric,
                    "offsets": src.offsets,
                    "name": src.name,
                    "colorinterp": src.colorinterp,
                    "resolution": src.res,
                    "statistics": [
                        {
                            "min": s.min,
                            "max": s.max,
                            "mean": s.mean,
                            "std": s.std,
                        }
                        for s in stats
                    ],
                }

                # Add HTTP headers to metadata if present
                http_headers = self._get_http_headers()
                if http_headers:
                    metadata["http_headers"] = http_headers

                self.metadata = metadata
                self.last_sync = {"timestamp": now(), "status": "ok"}
                self.save(update_fields=["metadata", "last_sync"])
        except RasterioError as e:
            self.last_sync = {"status": "fail", "timestamp": now(), "error": str(e)}
            self.metadata = {}
            self.save(update_fields=["last_sync", "metadata"])

    def get_edit_url(self):
        return reverse(
            "datasets:rasterresource_update",
            kwargs={"dataset_pk": self.dataset_id, "pk": self.pk},
        )


class TabularResource(Resource):
    name = models.CharField(
        null=True, blank=True, help_text="name of the layer if multiple are available"
    )

    @property
    def type(self):
        return "tabular"

    def infer_metadata(self, deferred=True):
        if deferred:
            app.configure_task(name="dms.datasets.tasks.infer_metadata_task").defer(
                resource_id=self.pk
            )
            return

        try:
            with fiona.open(
                self.uri,
                ignore_geometry=False,
                layer=self.name,
                driver=self.metadata.get("driver", None) if self.metadata else None,
            ) as src:
                geometry = (
                    src.schema["geometry"]
                    if src.schema.get("geometry") and src.schema["geometry"] != "None"
                    else None
                )
                metadata = {
                    "driver": src.driver,
                    "properties": src.schema["properties"],
                    "crs": src.crs.to_string(),
                    "geometry": geometry,
                    "tags": src.tags(),
                }

                if geometry:
                    metadata["bounds"] = src.bounds
                else:
                    metadata["bounds"] = None

                # Add HTTP headers to metadata if present
                http_headers = self._get_http_headers()
                if http_headers:
                    metadata["http_headers"] = http_headers

                self.metadata = metadata
                self.last_sync = {"timestamp": now(), "status": "ok"}
                self.save(update_fields=["metadata", "last_sync"])

        except fiona.errors.FionaError as e:
            self.last_sync = {"status": "fail", "timestamp": now(), "error": str(e)}
            self.metadata = {}
            self.save(update_fields=["last_sync", "metadata"])

    def get_edit_url(self):
        return reverse(
            "datasets:tabularresource_update",
            kwargs={"dataset_pk": self.dataset_id, "pk": self.pk},
        )


class PartitionedResource(Resource):
    name = models.CharField(
        null=True, blank=True, help_text="name of the layer if multiple are available"
    )

    @property
    def type(self):
        return "partitioned"

    def get_edit_url(self):
        return reverse(
            "datasets:partitionedresource_update",
            kwargs={"dataset_pk": self.dataset_id, "pk": self.pk},
        )
