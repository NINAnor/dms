from dal import autocomplete

from .models import Dataset


class DatasetAutocomplete(autocomplete.Select2QuerySetView):
    model = Dataset
    search_fields = [
        "name",
        "title",
    ]
