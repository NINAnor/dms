from django.urls import path

from . import views

app_name = "services"

urlpatterns = [
    path("services/", views.ServiceListView.as_view(), name="service_list"),
]
