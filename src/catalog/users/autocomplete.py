from dal import autocomplete

from .models import User


class UserAutocomplete(autocomplete.Select2QuerySetView):
    model = User
    search_fields = ["username", "email", "first_name", "last_name"]

    def get_result_value(self, result):
        return result.username
