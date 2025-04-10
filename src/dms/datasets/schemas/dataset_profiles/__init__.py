from django.db.models import TextChoices

from . import common, external


class DatasetProfileType(TextChoices):
    COMMON = "common", "Common"
    EXTERNAL = "external", "External"
    GBIF = "gbif", "GBIF"


DATASET_PROFILES_MAP = {
    DatasetProfileType.COMMON: common.schema,
    DatasetProfileType.EXTERNAL: external.schema,
    DatasetProfileType.GBIF: None,
}

__all__ = [
    "DatasetProfileType",
    "DATASET_PROFILES_MAP",
]
