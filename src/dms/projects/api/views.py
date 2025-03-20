from rest_framework.pagination import LimitOffsetPagination
from rest_framework.viewsets import GenericViewSet, mixins
from rules.contrib.rest_framework import AutoPermissionViewSetMixin

from ..filters import ProjectFilter
from ..models import Project
from .serializers import ProjectSerializer, ProjectUpdateSerializer


class ProjectModelViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    AutoPermissionViewSetMixin,
    GenericViewSet,
):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    pagination_class = LimitOffsetPagination
    filterset_class = ProjectFilter

    def get_queryset(self):
        qs = super().get_queryset()

        return qs

    def get_serializer_class(self):
        if self.action in ["update", "partial_update"]:
            return ProjectUpdateSerializer
        return super().get_serializer_class()
