from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, EmailField
from django.utils.translation import gettext_lazy as _

from .managers import UserManager


class User(AbstractUser):
    """
    Default custom user model for Catalog.
    """

    email = EmailField(_("email address"), unique=True)
    username = None  # type: ignore
    first_name = CharField(max_length=200)
    last_name = CharField(max_length=200)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()
