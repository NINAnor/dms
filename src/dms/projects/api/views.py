from rest_framework.pagination import LimitOffsetPagination
from rest_framework.viewsets import GenericViewSet, mixins
from rules.contrib.rest_framework import AutoPermissionViewSetMixin

from ..filters import ProjectFilter
from ..models import DMP, Project
from .serializers import DMPSerializer, ProjectSerializer


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


class DMPModelViewSet(
    mixins.UpdateModelMixin,
    AutoPermissionViewSetMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    queryset = DMP.objects.all()
    serializer_class = DMPSerializer
    pagination_class = LimitOffsetPagination
