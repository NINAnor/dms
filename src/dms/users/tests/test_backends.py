from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model

from dms.users.backends import LDAPBackend

User = get_user_model()


@pytest.mark.django_db
def test_ldap_backend_resolves_email_to_synced_username():
    user = User.objects.create_user(
        username="ldap-user",
        email="user@example.com",
        password="testpass123",  # noqa: S106
    )

    with patch(
        "django_auth_ldap.backend.LDAPBackend.authenticate", return_value=user
    ) as ldap_authenticate:
        result = LDAPBackend().authenticate(
            None,
            username="user@example.com",
            password="testpass123",  # noqa: S106
            email="user@example.com",
        )

    assert result == user
    assert ldap_authenticate.call_args.kwargs["username"] == "ldap-user"
