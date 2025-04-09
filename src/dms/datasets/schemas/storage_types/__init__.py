from django.db.models import TextChoices

from . import httpfs, s3


class StorageType(TextChoices):
    HTTP = "http", "HTTP"
    S3 = "s3", "S3"


STORAGE_TYPE_MAP = {
    StorageType.HTTP: httpfs.schema,
    StorageType.S3: s3.schema,
}

__all__ = [
    "StorageType",
    "STORAGE_TYPE_MAP",
]
