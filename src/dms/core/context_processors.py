from django.conf import settings
from django.http import HttpRequest
from django.template import Context


def context_settings(request: HttpRequest) -> Context:
    return {
        "PROJECT_NAME": settings.PROJECT_NAME,
        "SENTRY_DSN": settings.SENTRY_DSN,
        "DUCKUI_URL": settings.DATASETS_DUCKUI_URL,
        "NINA_MAP_PREVIEW": settings.DATASETS_NINA_MAP_PREVIEW,
    }
