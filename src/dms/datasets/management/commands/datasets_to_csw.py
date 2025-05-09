from django.core.management.base import BaseCommand

from ...libs.csw import to_records


class Command(BaseCommand):
    def handle(self, *args, **options):
        to_records()
