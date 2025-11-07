import json
import traceback
import uuid
from urllib.parse import urlencode

import requests
import rules
from autoslug import AutoSlugField
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import GEOSGeometry, Polygon
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone as tz
from django.utils.functional import cached_property
from django.utils.timezone import now
from django.utils.translation import gettext as _
from django_jsonform.models.fields import ArrayField
from django_jsonform.models.fields import JSONField as JSONBField
from django_lifecycle import AFTER_SAVE, LifecycleModelMixin, hook
from django_lifecycle.conditions import WhenFieldHasChanged
from model_utils.managers import InheritanceManager
from osgeo import gdal  # type: ignore[import]
from procrastinate.contrib.django import app
from rules.contrib.models import RulesModel
from taggit.managers import TaggableManager

from dms.core.models import GenericStringTaggedItem

from .conf import settings
from .enums import RelationshipType
from .rules import (
    dataset_in_user_projects,
    resource_in_user_projects,
)
from .schemas import dataset_metadata

gdal.UseExceptions()


class Dataset(RulesModel):
    id = models.CharField(primary_key=True, default=uuid.uuid4)
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
    embargo_end_date = models.DateField(null=True, blank=True)
    contributors = models.ManyToManyField(
        "users.User", through="DatasetContribution", blank=True
    )
    tags = TaggableManager(through=GenericStringTaggedItem, blank=True)

    extent = gis_models.GeometryField(
        null=True,
        blank=True,
        verbose_name="Spatial Extent",
    )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("datasets:dataset_detail", kwargs={"pk": self.pk})

    def clone(self):
        """
        Create a clone of the current dataset.
        """
        old_instance = self

        # Create new instance with a new UUID
        new_instance = Dataset.objects.create(
            title=self.title,
            version=self.version,
            project=self.project,
            metadata=self.metadata,
            embargo_end_date=self.embargo_end_date,
        )

        # Copy many-to-many relationships
        # Tags
        for tag in old_instance.tags.all():
            new_instance.tags.add(tag)

        # Contributors (through DatasetContribution)
        for contribution in old_instance.contributor_roles.all():
            DatasetContribution.objects.create(
                dataset=new_instance, user=contribution.user, roles=contribution.roles
            )

        return new_instance

    def compute_extent(self):
        self.extent = None
        for r in self.resources.exclude(extent=None):
            if self.extent:
                self.extent = self.extent.union(r.extent)
            else:
                self.extent = r.extent

        if self.extent:
            self.extent = Polygon.from_bbox(self.extent.extent)

        self.save(update_fields=["extent"])

    @cached_property
    def under_embargo(self):
        return (
            self.embargo_end_date
            and self.embargo_end_date > tz.localtime(tz.now()).date()
        )

    class Meta:
        rules_permissions = {
            "add": rules.is_authenticated,
            "view": rules.always_allow,
            "change": dataset_in_user_projects,
            "delete": rules.is_staff,
        }


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


class ContributionType(models.TextChoices):
    """
    https://datacite-metadata-schema.readthedocs.io/en/4.6/appendices/appendix-1/contributorType/
    """

    PROJECT_LEADER = "ProjectLeader", "Project Leader"
    DATA_MANAGER = "DataManager", "Data Manager"
    DATA_COLLECTOR = "DataCollector", "Data Collector"
    DATA_CURATOR = "DataCurator", "Data Curator"
    PROJECT_MANAGER = "ProjectManager", "Project Manager"
    CONTACT_PERSON = "ContactPerson", "Contact Person"
    OTHER = "Other", "Other"
    PROJECT_MEMBER = "ProjectMember", "Project Member"
    RESEARCHER = "Researcher", "Researcher"

    @classmethod
    def SCHEMA(self):
        return {
            "type": "array",
            "uniqueItems": True,
            "items": {
                "type": "string",
                "choices": [
                    {"label": label, "value": value}
                    for value, label in ContributionType.choices
                ],
            },
        }


class DatasetContribution(RulesModel):
    pk = models.CompositePrimaryKey("dataset_id", "user_id")
    uuid = models.UUIDField(db_default=models.Func(function="gen_random_uuid"))
    dataset = models.ForeignKey(
        "Dataset", on_delete=models.CASCADE, related_name="contributor_roles"
    )
    user = models.ForeignKey(
        "users.User", on_delete=models.PROTECT, related_name="dataset_contributions"
    )
    roles = ArrayField(models.CharField(choices=ContributionType.choices), default=list)

    class Meta:
        rules_permissions = {
            "add": rules.is_authenticated,
            "view": rules.always_allow,
            "change": resource_in_user_projects,
            "delete": resource_in_user_projects,
        }


class Resource(LifecycleModelMixin, RulesModel):
    class Role(models.TextChoices):
        DATA = "data", "Data"
        PRESENTATION = "presentation", "Presentation"
        DOCUMENTATION = "documentation", "Documentation"
        METADATA = "metadata", "Metadata"
        RAW_DATA = "raw_data", "Raw Data"

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
    tags = TaggableManager(through=GenericStringTaggedItem, blank=True)

    extent = gis_models.GeometryField(null=True, blank=True)

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

    titiler = models.JSONField(
        default=dict, verbose_name="Titiler configuration", blank=True
    )

    @property
    def preview_url(self):
        params = {
            "colormap_name": "viridis",
            **self.titiler,
            "url": self.uri,
        }
        params = (
            [(k, v) for k, v in params.items()]
            + [
                (
                    "rescale",
                    f"{band['minimum']},{band['maximum']}",
                )
                for band in self.metadata["bands"]
            ]
            + [
                (
                    "bidx",
                    f"{band['band']}",
                )
                for band in self.metadata["bands"]
            ]
        )
        return settings.DATASETS_TITILER_URL + "/cog/preview/?" + urlencode(params)

    def infer_metadata(self, deferred=True):
        if deferred:
            app.configure_task(name="dms.datasets.tasks.infer_metadata_task").defer(
                resource_id=self.pk
            )
            return

        try:
            # Disable permenent auxillary files to prevent GDAL
            # creating a stats file with a remote resource
            with gdal.config_options({"GDAL_PAM_ENABLED": "NO"}):
                with gdal.Run(
                    "raster",
                    "info",
                    input=self.uri,
                    stats=True,
                ) as alg:
                    metadata = alg.Output()
                    # Add HTTP headers to metadata if present
                    http_headers = self._get_http_headers()
                    if http_headers:
                        metadata["http_headers"] = http_headers

                    self.metadata = metadata
                    self.last_sync = {"timestamp": now(), "status": "ok"}
                    self.extent = GEOSGeometry(json.dumps(metadata.get("wgs84Extent")))
                    self.save(update_fields=["metadata", "last_sync", "extent"])
        except Exception as e:
            self.last_sync = {"status": "fail", "timestamp": now(), "error": str(e)}
            self.metadata = {}
            self.extent = None
            self.save(update_fields=["last_sync", "metadata", "extent"])

    def get_edit_url(self):
        return reverse(
            "datasets:rasterresource_update",
            kwargs={"dataset_pk": self.dataset_id, "pk": self.pk},
        )


class DataTable(gis_models.Model):
    pk = models.CompositePrimaryKey("resource", "name")
    name = models.CharField()
    fields = JSONBField(default=list)
    metadata = JSONBField(default=dict)
    count = models.IntegerField(default=0)
    geometryFields = JSONBField(null=True, blank=True)
    resource = models.ForeignKey(
        "Resource", on_delete=models.CASCADE, related_name="data_tables"
    )
    extent = gis_models.GeometryField(null=True, blank=True)

    @property
    def is_spatial(self):
        return self.extent is not None


class TabularResource(Resource):
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
            with gdal.Run(
                "vector",
                "info",
                input=self.uri,
            ) as alg:
                metadata = alg.Output()

                # Add HTTP headers to metadata if present
                http_headers = self._get_http_headers()
                if http_headers:
                    metadata["http_headers"] = http_headers

                self.metadata = metadata
                self.last_sync = {"timestamp": now(), "status": "ok", "warnings": []}
                with transaction.atomic():
                    layers = self.metadata.get("layers", [])

                    tables = []
                    coverage = None
                    for layer in layers:
                        geometries = layer.get("geometryFields", [])
                        extent = None

                        try:
                            if len(geometries):
                                geom = geometries[0]

                                extent = Polygon.from_bbox(geom.get("extent"))
                                extent.srid = int(
                                    geom.get("coordinateSystem")
                                    .get("projjson")
                                    .get("id")
                                    .get("code")
                                )

                                if extent.srid != 4326:
                                    extent.transform(4326)

                                coverage = (
                                    extent if not coverage else coverage.union(extent)
                                )
                        except Exception:
                            self.last_sync["warnings"].append(traceback.format_exc())

                        tables.append(
                            DataTable(
                                name=layer.get("name").replace("_gdal_http_", ""),
                                fields=layer.get("fields", []),
                                metadata=layer.get("metadata", {}),
                                resource=self,
                                count=layer.get("featureCount"),
                                geometryFields=geometries,
                                extent=extent,
                            )
                        )

                    DataTable.objects.filter(resource=self).delete()
                    DataTable.objects.bulk_create(tables)

                    self.extent = coverage

                    self.save(update_fields=["metadata", "last_sync", "extent"])

        except Exception as e:
            self.last_sync = {"status": "fail", "timestamp": now(), "error": str(e)}
            self.metadata = {}
            self.extent = None
            self.save(update_fields=["last_sync", "metadata"])

    def get_edit_url(self):
        return reverse(
            "datasets:tabularresource_update",
            kwargs={"dataset_pk": self.dataset_id, "pk": self.pk},
        )


class PartitionedResource(Resource):
    """
    A resource that is represented by the union of multiple files.
    NOTE: GDAL does not support partioned datasets in vsis3
    """

    endpoint = models.CharField(null=True, blank=True)
    https = models.BooleanField(null=True, blank=True)
    path_style = models.CharField(
        choices=[("path", "path"), ("virtual", "virtual")], null=True, blank=True
    )

    @property
    def type(self):
        return "partitioned"

    def get_edit_url(self):
        return reverse(
            "datasets:partitionedresource_update",
            kwargs={"dataset_pk": self.dataset_id, "pk": self.pk},
        )
