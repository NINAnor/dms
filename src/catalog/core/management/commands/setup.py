import traceback

from countries_plus.models import Country
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand
from languages_plus.models import Language

User = get_user_model()


class Command(BaseCommand):
    def handle(self, *args, **options):
        if not User.objects.all().exists():
            call_command("loaddata", "users.json")

        if not Country.objects.all().exists():
            try:
                call_command("update_countries_plus")
            except Exception:
                print(traceback.format_exc())
                print("Falling back to local fixture")
            call_command("loaddata", "countries.json.gz")

        if not Language.objects.all().exists():
            call_command("loaddata", "languages_data.json.gz")
