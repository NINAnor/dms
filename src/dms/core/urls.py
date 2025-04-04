from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views import defaults as default_views

urlpatterns = [
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # User management
    path("accounts/", include("allauth.urls")),
    path("ht/", include("health_check.urls")),
    path("autocomplete/", include("dms.core.autocomplete", namespace="autocomplete")),
    path("api/v1/", include("dms.core.router", namespace="api_v1")),
    path("surveys/", include("dms.surveys.urls", namespace="surveys")),
    path("", include("dms.projects.urls", namespace="projects")),
    path("", include("dms.datasets.urls", namespace="datasets")),
    path("", include("dms.theme.urls")),
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
