from appconf import AppConf
from django.conf import settings  # noqa: F401


class DatasetsConf(AppConf):
    TITILER_URL = "/titiler"
