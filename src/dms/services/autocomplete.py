from dal import autocomplete

from .models import Service


class ServiceKeywordAutocomplete(autocomplete.Select2ListView):
    def get_list(self):
        return Service.objects.get_keywords_list()


class ServiceTechnologyAutocomplete(autocomplete.Select2ListView):
    def get_list(self):
        return Service.objects.get_technologies_list()
