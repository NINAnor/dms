from django.core.exceptions import ImproperlyConfigured
from django.middleware.csrf import get_token


class FrontendMixin:
    template_name = "frontend/base.html"
    frontend_module = ""

    def get_initial_data(self) -> dict:
        return {}

    def get_context_data(self, **kwargs) -> dict[str, any]:
        context = super().get_context_data(**kwargs)
        context["frontend_args"] = {
            "csrf": get_token(self.request),
            **self.get_initial_data(),
        }
        if not self.frontend_module:
            raise ImproperlyConfigured("Missing frontend module")
        context["frontend_module_path"] = f"src/{self.frontend_module}/main.tsx"
        return context
