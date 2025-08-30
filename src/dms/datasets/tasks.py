from django.db import close_old_connections
from procrastinate.contrib.django import app

from .models import RasterResource, TabularResource


@app.task
def infer_raster_metadata_task(resource_id: str):
    close_old_connections()
    try:
        resource = RasterResource.objects.get(id=resource_id)
        resource.infer_metadata(deferred=False)
    finally:
        close_old_connections()


@app.task
def infer_tabular_metadata_task(resource_id: str):
    close_old_connections()
    try:
        resource = TabularResource.objects.get(id=resource_id)
        resource.infer_metadata(deferred=False)
    finally:
        close_old_connections()


@app.periodic(cron="0 * * * *")
@app.task
def update_metadata(timestamp: int):
    close_old_connections()
    resources = TabularResource.objects.all()
    for resource in resources:
        resource.infer_metadata(deferred=False)

    close_old_connections()
    resources = RasterResource.objects.all()
    for resource in resources:
        resource.infer_metadata(deferred=False)
