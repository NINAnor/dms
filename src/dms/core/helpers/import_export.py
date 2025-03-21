from import_export import fields, widgets
from taggit.forms import TagField


class TagWidget(widgets.ManyToManyWidget):
    def render(self, value, obj=None):
        return self.separator.join([obj.name for obj in value.all()])

    def clean(self, value, row=None, *args, **kwargs):
        values = TagField().clean(value)
        return values


class TagFieldImport(fields.Field):
    def save(self, obj, data, is_m2m=False):
        # This method is overridden because originally code
        # getattr(obj, attrs[-1]).set(cleaned, clean=True) doesn't unpack cleaned value
        if not self.readonly:
            attrs = self.attribute.split("__")
            for attr in attrs[:-1]:
                obj = getattr(obj, attr, None)
            cleaned = self.clean(data)
            if cleaned is not None or self.saves_null_values:
                print(is_m2m, cleaned, attrs[-1])
                if not is_m2m:
                    setattr(obj, attrs[-1], cleaned)
                else:
                    # Change only here
                    getattr(obj, attrs[-1]).set(cleaned, clean=True)
