from django.urls import path

from . import views

app_name = "services"

urlpatterns = [
    path(
        "resources/",
        views.ServiceResourceListView.as_view(),
        name="resource_list",
    ),
    path("", views.ServiceListView.as_view(), name="service_list"),
    path("<str:pk>/", views.ServiceDetailView.as_view(), name="service_detail"),
]
