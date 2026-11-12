from django.db import close_old_connections
from procrastinate.contrib.django import app

from .models import Resource


@app.task
def infer_metadata_task(resource_id: str):
    close_old_connections()
    try:
        resource = Resource.objects.get_subclass(id=resource_id)
        resource.infer_metadata(deferred=False)
    finally:
        close_old_connections()


@app.task
def move_resource_to_storage_task(resource_id: str, target_storage_id: int):
    close_old_connections()
    try:
        from buckets.models import Storage

        resource = Resource.objects.get_subclass(id=resource_id)
        target_storage = Storage.objects.get(id=target_storage_id)

        # Move the object between storages using already-rendered S3 keys
        resource.storage.move_object_between_storages(
            source_key=resource.key,
            target_storage=target_storage,
            target_key=resource.key,  # Same key in target storage
        )

        # Update resource with new storage and location
        resource.storage = target_storage
        resource.uri = target_storage.get_http_url(resource.key)
        resource.save(update_fields=["storage", "uri"])
    finally:
        close_old_connections()


@app.periodic(cron="0 * * * *")
@app.task
def update_metadata(timestamp: int):
    close_old_connections()
    resources = Resource.objects.select_subclasses().filter(is_metadata_manual=False)
    for resource in resources:
        resource.infer_metadata(deferred=False)
        close_old_connections()
