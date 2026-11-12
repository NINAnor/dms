"""Tests for django-tasks task definitions in dms.core.tasks."""

from unittest.mock import patch

import pytest
from django.test import override_settings

from dms.core.tasks import sync_ldap


@pytest.mark.django_db
@override_settings(AUTH_LDAP_SERVER_URI="ldap://example.com")
def test_sync_ldap_calls_management_command_when_configured():
    """The task should invoke sync_ldap_users when LDAP is configured."""
    with patch("dms.core.tasks.call_command") as mocked_call_command:
        sync_ldap.call(timestamp=0)

    mocked_call_command.assert_called_once_with("sync_ldap_users")


@pytest.mark.django_db
@override_settings(AUTH_LDAP_SERVER_URI="")
def test_sync_ldap_skips_management_command_when_not_configured():
    """The task should do nothing when LDAP is not configured."""
    with patch("dms.core.tasks.call_command") as mocked_call_command:
        sync_ldap.call(timestamp=0)

    mocked_call_command.assert_not_called()
