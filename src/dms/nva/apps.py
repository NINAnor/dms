from django.apps.config import AppConfig
from django.utils.translation import gettext_lazy as _


class NVAConfig(AppConfig):
    verbose_name = _("NVA")
    name = "dms.nva"
