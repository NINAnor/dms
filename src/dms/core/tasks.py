from crontask import cron
from django.conf import settings
from django.core.management import call_command
from django.db import close_old_connections
from django.tasks import task


@cron("* 0 * * *")
@task
def sync_ldap(timestamp: int):
    close_old_connections()
    if settings.AUTH_LDAP_SERVER_URI:
        call_command("sync_ldap_users")
