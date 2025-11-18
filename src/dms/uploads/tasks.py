from django.db import close_old_connections
from procrastinate.contrib.django import app

from .models import HookRequest


@app.task
def process_upload(upload_id: str):
    close_old_connections()
    try:
        HookRequest.objects.get(id=upload_id).process()
    finally:
        close_old_connections()
