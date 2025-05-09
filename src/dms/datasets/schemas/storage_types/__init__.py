from django.db.models import TextChoices

from . import httpfs, network_storage, s3
from .base import StorageBase


class StorageType(TextChoices):
    HTTP = "http", "HTTP"
    S3 = "s3", "S3"
    NFS = "nfs", "Shared FileSystem (P:, R:)"


STORAGE_TYPE_MAP = {
    StorageType.HTTP: httpfs.HTTPFSStorage,
    StorageType.S3: s3.SimpleObjectStorage,
    StorageType.NFS: network_storage.NetworkStorage,
}

__all__ = ["StorageType", "STORAGE_TYPE_MAP", "StorageBase"]
