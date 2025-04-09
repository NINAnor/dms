from django.db.models import TextChoices

from ..resource_profiles import ResourceProfileType
from . import cog, notes, parquet


class ResourceType(TextChoices):
    PARQUET = "parquet", "Parquet"
    # CSV = "text/csv", "CSV" # Should be supported?
    # JSON = "application/json", "JSON"
    # # It's probably needed for nested/unstructured data
    COG = (
        "cloud-optimized-geotiff",
        "Cloud Optimized GeoTIFF",
    )
    DWCA = "dwca", "Darwin Core Archive"
    PDF = "pdf", "PDF"
    OTHER = "", "Other"


RESOURCE_TYPE_MAP = {
    ResourceProfileType.TABULAR: {
        ResourceType.PARQUET: parquet.schema,
    },
    ResourceProfileType.VECTOR: {
        ResourceType.PARQUET: parquet.geo_schema,
        ResourceType.DWCA: notes.schema,
    },
    ResourceProfileType.RASTER: {
        ResourceType.COG: cog.schema,
    },
    ResourceProfileType.DOCUMENTATION: {
        ResourceType.PDF: notes.schema,
        ResourceType.OTHER: notes.schema,
    },
}

__all__ = [
    "ResourceType",
    "RESOURCE_TYPE_MAP",
]
