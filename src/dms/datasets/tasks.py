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


@app.periodic(cron="0 * * * *")
@app.task
def update_metadata(timestamp: int):
    close_old_connections()
    resources = Resource.objects.select_subclasses().all()
    for resource in resources:
        resource.infer_metadata(deferred=False)
        close_old_connections()
