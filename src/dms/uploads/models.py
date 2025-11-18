import uuid

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils.timezone import now
from django_lifecycle import LifecycleModel

from dms.datasets.models import (
    Dataset,
    Resource,
)


class HookRequest(LifecycleModel):
    id = models.CharField(primary_key=True, default=uuid.uuid4)
    event = models.JSONField(encoder=DjangoJSONEncoder)
    created_at = models.DateTimeField(auto_now_add=True)
    type = models.CharField()
    completed_at = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(
        "users.User", on_delete=models.SET_NULL, null=True, blank=True
    )

    def process(self):
        metadata = self.event.get("Upload").get("MetaData")
        dataset = Dataset.objects.get(id=metadata.get("dataset"))
        source_key = self.event.get("Upload").get("Storage").get("Key")
        dest_key = f"project/{dataset.project_id}/datasets/{dataset.id}/{metadata.get('filename')}"  # noqa: E501

        if settings.AWS_ACCESS_KEY_ID:
            from dms.core.helpers.s3client import s3client

            s3client.copy_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                CopySource={
                    "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
                    "Key": source_key,
                },
                Key=f"{settings.MEDIA_BASE_LOCATION}/{dest_key}",
            )

            Resource.objects.create(
                id=self.event.get("Upload").get("ID"),
                metadata={},
                dataset=dataset,
                title=metadata.get("filename"),
                uri=settings.MEDIA_URL + dest_key,
            )

            self.completed_at = now()
            self.save(update_fields=["completed_at"])
            s3client.delete_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=source_key
            )
