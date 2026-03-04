from django.views.generic import TemplateView

from dms.services.models import Resource


class HomeView(TemplateView):
    template_name = "theme/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["featured_resources"] = Resource.objects.filter(featured=True).order_by(
            "featured_order"
        )
        return context
