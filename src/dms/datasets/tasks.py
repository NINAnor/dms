from crontask import cron
from django.db import close_old_connections
from django.tasks import task

from .models import Resource


@task
def infer_metadata_task(resource_id: str):
    close_old_connections()
    try:
        resource = Resource.objects.get_subclass(id=resource_id)
        resource.infer_metadata(deferred=False)
    finally:
        close_old_connections()


@cron("0 * * * *")
@task
def update_metadata(timestamp: int):
    close_old_connections()
    resources = Resource.objects.select_subclasses().filter(is_metadata_manual=False)
    for resource in resources:
        resource.infer_metadata(deferred=False)
        close_old_connections()
