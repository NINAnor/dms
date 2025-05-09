import logging

from django.core.management.base import BaseCommand

from ...conf import settings
from ...libs.harvesters import ipt


class Command(BaseCommand):
    def handle(self, *args, **options):
        harvester = ipt.IPTHarvester()
        for url in settings.DATASETS_IPT_URLS:
            logging.info(f"fetching {url}")
            harvester.run(url=url)
