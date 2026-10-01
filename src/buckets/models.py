"""The ``buckets`` app: a standalone, Django-app-only wrapper around an
S3-compatible bucket/endpoint.

This module must never import from any other app in this project (no
``dms.*`` imports). It is designed to be extractable into its own
pip-installable package.
"""

import boto3
from botocore.client import Config
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_cryptography.fields import encrypt


class CannedACL(models.TextChoices):
    PRIVATE = "private", _("Private")
    PUBLIC_READ = "public-read", _("Public read")
    PUBLIC_READ_WRITE = "public-read-write", _("Public read/write")
    AUTHENTICATED_READ = "authenticated-read", _("Authenticated read")


class Storage(models.Model):
    """A single S3-compatible bucket/endpoint + credentials."""

    name = models.CharField(max_length=255)

    endpoint_url = models.CharField(
        max_length=255,
        blank=True,
        help_text=_(
            "Custom S3-compatible endpoint URL (e.g. MinIO/RustFS). "
            "Leave blank to use real AWS S3."
        ),
    )
    region = models.CharField(max_length=64, blank=True, null=True)
    bucket_name = models.CharField(max_length=255)

    access_key_id = encrypt(models.CharField(max_length=512))
    secret_access_key = encrypt(models.CharField(max_length=512))

    prefix = models.CharField(max_length=255, blank=True)

    canned_acl = models.CharField(
        max_length=32,
        choices=CannedACL,
        default=CannedACL.PRIVATE,
    )

    is_global = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Storage")
        verbose_name_plural = _("Storages")

    def __str__(self):
        return self.name

    # -- internals ---------------------------------------------------

    def _client(self):
        config = Config(signature_version="s3v4")
        return boto3.client(
            "s3",
            endpoint_url=self.endpoint_url or None,
            region_name=self.region or None,
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
            config=config,
        )

    def _render(self, template: str, **context) -> str:
        if not template:
            return ""
        try:
            return template.format(**context)
        except (KeyError, IndexError):
            return template

    def _is_public(self) -> bool:
        return self.canned_acl in (
            CannedACL.PUBLIC_READ,
            CannedACL.PUBLIC_READ_WRITE,
        )

    # -- public API ----------------------------------------------------

    def get_s3_path(self, key: str, **context) -> str:
        """Render this storage's prefix template and join it with ``key``.

        ``prefix`` is an unvalidated template string (e.g.
        ``"{project_id}/{dataset_id}"``) rendered against whatever
        ``**context`` kwargs the caller supplies.
        """
        prefix = self._render(self.prefix, **context).strip("/")
        return f"{prefix}/{key}" if prefix else key

    def get_http_url(self, key: str, expires_in: int = 3600, **context) -> str:
        """Return a URL to GET ``key`` (plain if public, presigned otherwise)."""
        path = self.get_s3_path(key, **context)
        if self._is_public():
            if self.endpoint_url:
                return f"{self.endpoint_url.rstrip('/')}/{self.bucket_name}/{path}"
            return f"https://{self.bucket_name}.s3.amazonaws.com/{path}"
        return self._client().generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket_name, "Key": path},
            ExpiresIn=expires_in,
        )

    def get_presigned_upload_url(
        self, key: str, expires_in: int = 3600, **context
    ) -> str:
        """Return a single-part presigned PUT URL for uploading to ``key``."""
        path = self.get_s3_path(key, **context)
        return self._client().generate_presigned_url(
            "put_object",
            Params={
                "Bucket": self.bucket_name,
                "Key": path,
                "ACL": self.canned_acl,
            },
            ExpiresIn=expires_in,
        )

    def head_object(self, key: str, **context) -> dict | None:
        """Return the object's metadata if it exists in this storage, else None."""
        path = self.get_s3_path(key, **context)
        try:
            return self._client().head_object(Bucket=self.bucket_name, Key=path)
        except self._client().exceptions.ClientError:
            return None

    # -- multipart upload lifecycle --------------------------------------

    def create_multipart_upload(self, key: str, **context) -> dict:
        """Initiate a multipart upload; returns {"key": ..., "upload_id": ...}."""
        path = self.get_s3_path(key, **context)
        response = self._client().create_multipart_upload(
            Bucket=self.bucket_name, Key=path, ACL=self.canned_acl
        )
        return {"key": path, "upload_id": response["UploadId"]}

    def get_presigned_part_upload_url(
        self, key: str, upload_id: str, part_number: int, expires_in: int = 3600
    ) -> str:
        """Return a presigned PUT URL for a single part of a multipart upload.

        ``key`` here is expected to already be the fully-rendered S3 path, as
        returned by ``create_multipart_upload``.
        """
        return self._client().generate_presigned_url(
            "upload_part",
            Params={
                "Bucket": self.bucket_name,
                "Key": key,
                "UploadId": upload_id,
                "PartNumber": part_number,
            },
            ExpiresIn=expires_in,
        )

    def complete_multipart_upload(
        self, key: str, upload_id: str, parts: list[dict]
    ) -> dict:
        """Finish a multipart upload.

        ``key`` is the fully-rendered S3 path. ``parts`` is a list of
        ``{"ETag": ..., "PartNumber": ...}`` dicts, one per uploaded part.
        """
        return self._client().complete_multipart_upload(
            Bucket=self.bucket_name,
            Key=key,
            UploadId=upload_id,
            MultipartUpload={"Parts": parts},
        )

    def abort_multipart_upload(self, key: str, upload_id: str) -> None:
        self._client().abort_multipart_upload(
            Bucket=self.bucket_name, Key=key, UploadId=upload_id
        )
