from django.apps import AppConfig as DjangoAppConfig
from django.utils.translation import gettext_lazy as _


class UploadsConfig(DjangoAppConfig):
    name = "dms.uploads"
    verbose_name = _("Uploads")
