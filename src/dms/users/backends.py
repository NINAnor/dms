from django.contrib.auth import get_user_model
from django_auth_ldap.backend import LDAPBackend as DjangoLDAPBackend


class LDAPBackend(DjangoLDAPBackend):
    """Authenticate email logins against LDAP using the synced username."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        email = kwargs.get("email")
        if email and username == email:
            User = get_user_model()
            try:
                user = User.objects.get(email__iexact=email)
            except (User.DoesNotExist, User.MultipleObjectsReturned):
                # Keep the original value for LDAP directories keyed by email.
                pass
            else:
                username = user.get_username()

        return super().authenticate(
            request,
            username=username,
            password=password,
            **kwargs,
        )
