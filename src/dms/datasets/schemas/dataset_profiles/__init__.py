from django.db.models import TextChoices

from . import datacite


class DatasetProfileType(TextChoices):
    DATACITE = "datacite", "DataCite"
    GBIF = "gbif", "GBIF"


DATASET_PROFILES_MAP = {
    DatasetProfileType.DATACITE: datacite.schema,
    # it's not possible to create manually a GBIF EML metadata
    # might be solved in a future
    DatasetProfileType.GBIF: None,
}

__all__ = [
    "DatasetProfileType",
    "DATASET_PROFILES_MAP",
]
