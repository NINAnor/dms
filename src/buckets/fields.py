"""Symmetric-encryption model field for storing credentials at rest.

Deliberately dependency-light (stdlib ``cryptography`` only) so this module
has no coupling to any other app. The encryption key is read from the
``STORAGE_CREDENTIALS_KEY`` Django setting, expected to be a urlsafe-base64
Fernet key (see ``cryptography.fernet.Fernet.generate_key()``).
"""

from functools import lru_cache

from cryptography.fernet import Fernet
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models


@lru_cache(maxsize=1)
def _get_fernet() -> Fernet:
    key = getattr(settings, "STORAGE_CREDENTIALS_KEY", None)
    if not key:
        raise ImproperlyConfigured(
            "STORAGE_CREDENTIALS_KEY must be set to encrypt/decrypt "
            "buckets.Storage credential fields."
        )
    return Fernet(key if isinstance(key, bytes) else key.encode())


class EncryptedCharField(models.CharField):
    """A CharField that is transparently encrypted at rest.

    Stored values are encrypted Fernet tokens; `to_python`/`from_db_value`
    decrypt them back to plain strings for use in Python.
    """

    def get_internal_type(self):
        return "TextField"

    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname)
        if value in (None, ""):
            return value
        token = _get_fernet().encrypt(value.encode()).decode()
        setattr(model_instance, self.attname, value)
        return token

    def from_db_value(self, value, expression, connection):
        if value in (None, ""):
            return value
        return _get_fernet().decrypt(value.encode()).decode()
