"""
The resource profile describes the schema of the data contained in the resource.
"""

from django.db.models import TextChoices

from . import raster, tabular


class ResourceProfileType(TextChoices):
    TABULAR = "tabular", "Tabular"
    VECTOR = "vector", "Vector"
    RASTER = "raster", "Raster"
    DOCUMENTATION = "documentation", "Documentation"


RESOURCE_PROFILES_MAP = {
    ResourceProfileType.TABULAR: tabular.schema,
    ResourceProfileType.VECTOR: tabular.schema,
    ResourceProfileType.RASTER: raster.schema,
    ResourceProfileType.DOCUMENTATION: None,
}

__all__ = [
    "ResourceProfileType",
    "RESOURCE_PROFILES_MAP",
]
