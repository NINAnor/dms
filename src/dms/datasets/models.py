import rules
from autoslug import AutoSlugField
from django.contrib.gis.db import models as geo_models
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext as _
from django_jsonform.models.fields import JSONField as JSONBField
from jsonfield import JSONField
from rules.contrib.models import RulesModel, RulesModelBase, RulesModelMixin

from .rules import dataset_in_user_projects, resource_in_user_projects
from .schemas import DATASET_PROFILES, DatasetProfileType, ResourceProfileType


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
    return DATASET_PROFILES.get(instance.profile)


class Dataset(RulesModelMixin, geo_models.Model, metaclass=RulesModelBase):
    id = models.UUIDField(primary_key=True)
    title = models.CharField()
    name = AutoSlugField(populate_from="title")
    project = models.ForeignKey(
        "projects.Project", on_delete=models.PROTECT, related_name="datasets"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    last_modified_at = models.DateTimeField(
        auto_now=True, verbose_name=_("Last modified at")
    )
    profile = models.CharField(
        default=DatasetProfileType.COMMON, choices=DatasetProfileType.choices
    )
    metadata = JSONBField(schema=get_metadata_schema, default=dict)

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


class Resource(RulesModel):
    id = models.UUIDField(primary_key=True)
    title = models.CharField()
    name = AutoSlugField(populate_from="title")
    path = models.CharField()
    dataset = models.ForeignKey("Dataset", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    last_modified_at = models.DateTimeField(
        auto_now=True, verbose_name=_("Last modified at")
    )
    sources = models.ManyToManyField("self", blank=True)
    profile = models.CharField(
        choices=ResourceProfileType.choices, null=True, blank=True
    )
    metadata = JSONBField(default=dict)
    config = JSONBField(default=dict)

    class Meta:
        rules_permissions = {
            "add": rules.is_authenticated,
            "view": rules.always_allow,
            "change": resource_in_user_projects,
            "delete": rules.is_staff,
        }
