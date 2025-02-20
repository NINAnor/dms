from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, EmailField
from django.utils.translation import gettext_lazy as _

from .managers import UserManager


class User(AbstractUser):
    """
    Default custom user model for Catalog.
    """

    email = EmailField(_("email address"), unique=True, null=True, blank=True)
    first_name = CharField(max_length=200)
    last_name = CharField(max_length=200)

    objects = UserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
