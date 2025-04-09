from django.db.models import TextChoices

from . import common, external


class DatasetProfileType(TextChoices):
    COMMON = "common", "Common"
    EXTERNAL = "external", "External"


DATASET_PROFILES_MAP = {
    DatasetProfileType.COMMON: common.schema,
    DatasetProfileType.EXTERNAL: external.schema,
}

__all__ = [
    "DatasetProfileType",
    "DATASET_PROFILES_MAP",
]
