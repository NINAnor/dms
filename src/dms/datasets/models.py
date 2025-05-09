import rules
from autoslug import AutoSlugField
from django.contrib.gis.db import models as geo_models
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext as _
from django_jsonform.models.fields import JSONField as JSONBField
from jsonfield import JSONField
from procrastinate.contrib.django import app
from rules.contrib.models import RulesModel, RulesModelBase, RulesModelMixin

from . import schemas
from .libs import inference
from .rules import (
    dataset_in_user_projects,
    resource_in_user_projects,
    storage_in_user_projects,
    storage_is_shared,
)


class Schema(RulesModel):
    name = models.SlugField(primary_key=True)
    url = models.CharField(null=True, blank=True)
    schema = JSONField(default=dict)

    class Meta:
        rules_permissions = {
            "add": rules.is_staff,
            "view": rules.always_allow,
            "change": rules.is_staff,
            "delete": rules.is_staff,
        }

    def __str__(self):
        return self.name


def get_metadata_schema(instance=None):
    if not instance:
        return None
    return schemas.dataset_profiles.DATASET_PROFILES_MAP.get(instance.profile)


class Dataset(RulesModelMixin, geo_models.Model, metaclass=RulesModelBase):
    id = models.UUIDField(
        primary_key=True, db_default=models.Func(function="gen_random_uuid")
    )
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
    profile = models.CharField(
        default=schemas.dataset_profiles.DatasetProfileType.DATACITE,
        choices=schemas.dataset_profiles.DatasetProfileType.choices,
    )
    metadata = JSONBField(
        schema=get_metadata_schema, default=dict, encoder=DjangoJSONEncoder
    )
    fetch = JSONBField(null=True, blank=True, encoder=DjangoJSONEncoder)
    version = models.IntegerField(null=True, blank=True)

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

    def fetch_updates(self):
        if self.fetch:
            app.configure_task(name=self.fetch["task_name"]).defer(
                dataset_id=str(self.id)
            )


class RelationshipType(models.TextChoices):
    CITES = "Cites", "Cites"
    REFERENCES = "References", "References"
    IS_PART_OF = "IsPartOf", "Is part of"
    IS_SOURCE_OF = "IsSourceOf", "Is source of"
    IS_DERIVED_FROM = "IsDerivedFrom", "Is derived from"
    IS_TRANSLATION_OF = "IsTranslationOf", "Is translation of"
    REVIEWS = "Reviews", "Reviews"
    DOCUMENTS = "Documents", "Documents"


class DatasetRelationship(RulesModel):
    id = models.UUIDField(
        primary_key=True, db_default=models.Func(function="gen_random_uuid")
    )
    source = models.ForeignKey(
        "Dataset", on_delete=models.CASCADE, related_name="source_rels"
    )
    destination = models.ForeignKey(
        "Dataset", on_delete=models.CASCADE, related_name="dest_rels"
    )
    type = models.CharField(choices=RelationshipType.choices)

    class Meta:
        rules_permissions = {
            "add": rules.is_authenticated,
            "view": rules.always_allow,
            "change": rules.is_authenticated,
            "delete": rules.is_authenticated,
        }
        constraints = [
            models.UniqueConstraint(
                fields=["source", "destination", "type"],
                name="unique_relationship_type",
            )
        ]


def get_config_schema(instance=None):
    if not instance:
        return None
    return instance.get_schema()


class Storage(RulesModel):
    id = models.UUIDField(
        primary_key=True, db_default=models.Func(function="gen_random_uuid")
    )
    title = models.CharField()
    type = models.CharField(choices=schemas.storage_types.StorageType.choices)
    config = JSONBField(null=True, blank=True, schema=get_config_schema)
    created_at = models.DateTimeField(
        db_default=models.functions.Now(), verbose_name=_("Created at")
    )
    last_modified_at = models.DateTimeField(
        auto_now=True, verbose_name=_("Last modified at")
    )
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.PROTECT,
        related_name="storages",
        null=True,
        blank=True,
    )

    class Meta:
        rules_permissions = {
            "add": rules.is_authenticated,
            "view": storage_in_user_projects | storage_is_shared,
            "change": storage_in_user_projects,
            "delete": rules.is_staff,
        }

    def get_absolute_url(self):
        return reverse(
            "datasets:storage_detail",
            kwargs={"pk": self.pk},
        )

    def _get_type_class(self) -> schemas.storage_types.StorageBase:
        return schemas.storage_types.STORAGE_TYPE_MAP.get(self.type)

    def get_full_path(self, path: str):
        cls: schemas.storage_types.base.StorageBase = self._get_type_class()
        return cls.get_full_path(self.config, path)

    def get_schema(self):
        cls: schemas.storage_types.base.StorageBase = self._get_type_class()
        return cls.SCHEMA

    def __str__(self):
        return self.title


def get_resource_metadata_schema(instance=None):
    if not instance:
        return None
    return schemas.resource_types.RESOURCE_TYPE_MAP.get(instance.profile).get(
        instance.type
    )


def get_resource_data_schema(instance=None):
    if not instance:
        return None
    return schemas.resource_profiles.RESOURCE_PROFILES_MAP.get(instance.profile, None)


class Resource(RulesModel):
    id = models.UUIDField(
        primary_key=True, db_default=models.Func(function="gen_random_uuid")
    )
    title = models.CharField(help_text="A name that describes the resource")
    name = AutoSlugField(populate_from="title")
    path = models.CharField(
        verbose_name="Path to the resource",
        help_text="describe how to find the resource."
        + " Can be a link, or a path relative to the selected storage",
    )
    storage = models.ForeignKey(
        "Storage",
        on_delete=models.CASCADE,
        related_name="resources",
        null=True,
        blank=True,
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
    profile = models.CharField(
        choices=schemas.resource_profiles.ResourceProfileType.choices,
        null=True,
        blank=True,
        help_text="To what profile should this resouce conform to?",
    )
    type = models.CharField(
        choices=schemas.resource_types.ResourceType,
        default=schemas.resource_types.ResourceType.OTHER,
    )
    metadata = JSONBField(
        default=dict, schema=get_resource_metadata_schema, encoder=DjangoJSONEncoder
    )
    schema = JSONBField(
        default=dict, schema=get_resource_data_schema, encoder=DjangoJSONEncoder
    )

    class Meta:
        rules_permissions = {
            "add": rules.is_authenticated,
            "view": rules.always_allow,
            "change": resource_in_user_projects,
            "delete": rules.is_staff,
        }

    def get_absolute_url(self):
        return reverse(
            "datasets:resource_detail",
            kwargs={"dataset_pk": self.dataset_id, "pk": self.pk},
        )

    def __str__(self):
        return self.title

    def get_resource_path(self):
        if not self.storage:
            return self.path

        return self.storage.get_full_path(self.path)

    def infer_schema(self) -> bool:
        if self.type == schemas.resource_types.ResourceType.PARQUET:
            path = self.get_resource_path()
            self.schema["columns"] = inference.duckdb_inference(path)
            self.save(update_fields=["schema"])
            return True

        return False
