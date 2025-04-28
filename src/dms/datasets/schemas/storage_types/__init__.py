from django.db.models import TextChoices

from . import httpfs, network_storage, s3


class StorageType(TextChoices):
    HTTP = "http", "HTTP"
    S3 = "s3", "S3"
    NFS = "nfs", "Shared FileSystem (P:, R:)"


STORAGE_TYPE_MAP = {
    StorageType.HTTP: httpfs.schema,
    StorageType.S3: s3.schema,
    StorageType.NFS: network_storage.schema,
}

__all__ = [
    "StorageType",
    "STORAGE_TYPE_MAP",
]
