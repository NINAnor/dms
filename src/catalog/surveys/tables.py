import django_tables2 as tables

from .models import Survey


class SurveyTable(tables.Table):
    id = tables.LinkColumn()

    class Meta:
        model = Survey
        fields = (
            "id",
            "name",
            "creator",
            "created",
            "updated",
        )
