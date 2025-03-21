from django.db import models
from django.utils.translation import gettext_lazy as _
from taggit.models import CommonGenericTaggedItemBase, TaggedItemBase


class GenericStringTaggedItem(CommonGenericTaggedItemBase, TaggedItemBase):
    object_id = models.CharField(
        max_length=50, verbose_name=_("Object id"), db_index=True
    )
