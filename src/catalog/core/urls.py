from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views import defaults as default_views

from .views import HomeView

urlpatterns = [
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # User management
    path("accounts/", include("allauth.urls")),
    path("ht/", include("health_check.urls")),
    path(
        "autocomplete/", include("catalog.core.autocomplete", namespace="autocomplete")
    ),
    path("surveys/", include("catalog.surveys.urls", namespace="surveys")),
    path("", include("catalog.projects.urls", namespace="projects")),
    path("", HomeView.as_view(), name="home"),
]


if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
