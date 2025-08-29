from django.db import close_old_connections
from procrastinate.contrib.django import app

from .models import RasterResource, TabularResource


@app.periodic(cron="0 * * * *")
@app.task
def update_metadata(timestamp: int):
    close_old_connections()
    resources = TabularResource.objects.all()
    for resource in resources:
        resource.infer_metadata()

    close_old_connections()
    resources = RasterResource.objects.all()
    for resource in resources:
        resource.infer_metadata()
