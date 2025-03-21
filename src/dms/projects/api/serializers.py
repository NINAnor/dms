from rest_framework import serializers

from ..models import DMP, Project


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
        ]


class DMPSerializer(serializers.ModelSerializer):
    class Meta:
        model = DMP
        fields = [
            "id",
            "name",
            "data",
        ]
