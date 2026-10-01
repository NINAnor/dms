from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class BucketsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "buckets"
    verbose_name = _("Buckets")
