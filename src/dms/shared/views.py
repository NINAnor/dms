from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseRedirect
from django.views.generic.detail import (
    BaseDetailView,
    SingleObjectTemplateResponseMixin,
)


class ActionView(SingleObjectTemplateResponseMixin, BaseDetailView):
    """
    View for executing a method of an object retrieved with self.get_object(), with a
    response rendered by a template.
    """

    success_url = None

    def get_success_url(self):
        if self.success_url:
            return self.success_url.format(**self.object.__dict__)
        else:
            raise ImproperlyConfigured("No URL to redirect to. Provide a success_url.")

    def execute(self):
        raise NotImplementedError()

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        return HttpResponseRedirect(success_url)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.execute()
        success_url = self.get_success_url()
        return HttpResponseRedirect(success_url)
