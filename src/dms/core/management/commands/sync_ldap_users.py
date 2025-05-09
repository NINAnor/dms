import logging
import traceback

import ldap
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from ldap.controls import SimplePagedResultsControl


def get_string(entry, attribute):
    return entry.get(attribute, [b""])[0].decode("utf-8").strip()


PAGE_SIZE = 50


class Command(BaseCommand):
    help = "Sync users from LDAP to Django"

    def handle(self, *args, **kwargs):
        User = get_user_model()

        try:
            # Connect to LDAP server
            ldap_connection = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
            ldap_connection.simple_bind_s(
                settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD
            )

            page_control = SimplePagedResultsControl(True, PAGE_SIZE, "")

            attrs = [
                *settings.AUTH_LDAP_USER_ATTR_MAP.values(),
                settings.AUTH_LDAP_UID,
            ]

            while True:
                msgid = ldap_connection.search_ext(
                    settings.AUTH_LDAP_USER_SEARCH_BASE,
                    ldap.SCOPE_SUBTREE,
                    "(&(objectClass=user)(objectClass=person))",
                    attrs,
                    serverctrls=[page_control],
                )
                rtype, rdata, rmsgid, serverctrls = ldap_connection.result3(msgid)

                for _dn, entry in rdata:
                    if not entry:
                        continue

                    username = get_string(entry, settings.AUTH_LDAP_UID)
                    user_id = get_string(entry, settings.AUTH_LDAP_USER_ATTR_MAP["id"])
                    defaults = {}

                    for k, m in settings.AUTH_LDAP_USER_ATTR_MAP.items():
                        defaults[k] = get_string(entry, m)

                    if not all(defaults.values()) or not username or not user_id:
                        logging.warning(
                            f"Skipping {username} as some fields are empty: {str(defaults)}"  # noqa: E501
                        )
                        continue
                    else:
                        defaults["username"] = username

                    try:
                        with transaction.atomic():
                            user, created = User.objects.update_or_create(
                                id=user_id,
                                defaults=defaults,
                            )

                            if created:
                                user.set_unusable_password()
                                user.save()
                                self.stdout.write(f"Created new user: {username}")
                            else:
                                self.stdout.write(f"Updated user: {username}")
                    except Exception:
                        logging.error(f"Error with {username}. Not importing")
                        logging.error(traceback.format_exc())

                # Check if more pages exist
                pctrls = [
                    ctrl
                    for ctrl in serverctrls
                    if ctrl.controlType == SimplePagedResultsControl.controlType
                ]
                if not pctrls or not pctrls[0].cookie:
                    break  # No more pages

                # Update the cookie for the next request
                page_control.cookie = pctrls[0].cookie

            self.stdout.write(self.style.SUCCESS("LDAP users imported successfully."))

        except ldap.LDAPError as e:
            self.stderr.write(f"LDAP Error: {e}")
