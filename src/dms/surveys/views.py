import json

from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import (
    CreateView,
    DetailView,
)
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from view_breadcrumbs import (
    CreateBreadcrumbMixin,
    DetailBreadcrumbMixin,
    ListBreadcrumbMixin,
)

from .forms import SurveyForm
from .models import Survey
from .tables import SurveyTable


class SurveyListView(ListBreadcrumbMixin, SingleTableMixin, FilterView):
    model = Survey
    filterset_fields = ["name"]
    table_class = SurveyTable


class SurveyDetailView(DetailBreadcrumbMixin, DetailView):
    model = Survey


class SurveyCreateView(CreateBreadcrumbMixin, CreateView):
    model = Survey
    form_class = SurveyForm

    def form_valid(self, form):
        survey = form.save()
        survey.creator = self.request.user
        survey.save()
        return HttpResponseRedirect(survey.get_absolute_url())


@login_required
@csrf_exempt
def survey_update_view(request, pk):
    try:
        survey = Survey.objects.filter(creator=request.user).get(pk=pk)
        survey.config = json.loads(request.body.decode("utf-8"))
        survey.save()
        return HttpResponse()
    except Survey.DoesNotExist:
        return Http404()
