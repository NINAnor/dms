from django.conf import settings
from django.core.management import call_command
from procrastinate.contrib.django import app


@app.periodic(cron="* 0 * * *")
@app.task(name="sync_ldap")
def sync_ldap(timestamp: int):
    if settings.AUTH_LDAP_SERVER_URI:
        call_command("sync_ldap_users")
