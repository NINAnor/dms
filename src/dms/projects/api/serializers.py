from rest_framework import serializers

from ..models import Project


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            "number",
            "description",
            "start_date",
            "end_date",
            "status",
            "category",
            "section",
            "customer",
            "dmp",
        ]


class ProjectUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            "description",
            "dmp",
        ]
