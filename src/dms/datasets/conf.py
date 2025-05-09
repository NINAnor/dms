from appconf import AppConf
from django.conf import settings  # noqa: F401


class DatasetsConf(AppConf):
    IPT_URLS = []
    IPT_CRON = "52 * * * *"
    CSW_PARQUET_PATH: str = ""
