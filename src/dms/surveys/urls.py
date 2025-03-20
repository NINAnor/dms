from django.urls import path

from .views import (
    SurveyCreateView,
    SurveyDetailView,
    SurveyListView,
    survey_update_view,
)

app_name = "surveys"

urlpatterns = [
    path("", SurveyListView.as_view(), name="survey_list"),
    path("<int:pk>/", SurveyDetailView.as_view(), name="survey_detail"),
    path("<int:pk>/update/", survey_update_view, name="survey_update"),
    path("create/", SurveyCreateView.as_view(), name="survey_create"),
]
