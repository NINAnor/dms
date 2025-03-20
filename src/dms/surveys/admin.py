from django.contrib import admin

from .models import Survey


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    pass
